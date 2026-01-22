#!/usr/bin/env python3
"""
Backfill script for daily_logs table using station history API
Fetches historical data from Deye Solar API and stores in daily_logs table
"""

import sqlite3
import requests
import json
import sys
import os
from datetime import datetime, timedelta
import time

# Add project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from clientcode import variable

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'solar_data.db')

def get_station_list():
    """Get list of stations"""
    url = variable.baseurl + '/station/list'
    headers = variable.headers
    data = {
        "page": 1,
        "size": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            return result.get('stationList', [])
        else:
            print(f"Error getting station list: {result.get('msg')}")
            return []
    except Exception as e:
        print(f"Exception getting station list: {e}")
        return []

def get_station_history(station_id, start_time, end_time):
    """Get station history data for a specific time range"""
    url = variable.baseurl + '/station/history'
    headers = variable.headers
    data = {
        "stationId": station_id,
        "granularity": 1,  # Frame-level data
        "startAt": start_time.split()[0],  # Extract date part only
        "endAt": end_time.split()[0]      # Extract date part only
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            return result.get('stationDataItems', [])
        else:
            print(f"Error getting station history: {result.get('msg')}")
            return []
    except Exception as e:
        print(f"Exception getting station history: {e}")
        return []

def convert_timestamp(timestamp):
    """Convert Unix timestamp to datetime string"""
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def map_api_to_db(station_data):
    """Map API response fields to database fields, converting watts to kilowatts"""
    return {
        'timestamp': convert_timestamp(station_data.get('timeStamp')),
        'production_kw': (station_data.get('generationPower') or 0) / 1000 if station_data.get('generationPower') is not None else None,
        'consumption_kw': (station_data.get('consumptionPower') or 0) / 1000 if station_data.get('consumptionPower') is not None else None,
        'grid_kw': (station_data.get('gridPower') or 0) / 1000 if station_data.get('gridPower') is not None else None,
        'battery_kw': (station_data.get('batteryPower') or 0) / 1000 if station_data.get('batteryPower') is not None else None,
        'soc_percent': station_data.get('batterySOC'),  # SOC remains as percentage
        'pv_kw': (station_data.get('generationPower') or 0) / 1000 if station_data.get('generationPower') is not None else None,  # Using generationPower as PV power
        'generator_kw': None,  # Not available in API response
        'grid_tied_inverter_power_kw': (station_data.get('wirePower') or 0) / 1000 if station_data.get('wirePower') is not None else None
    }

def backfill_daily_logs(station_id, start_date, end_date):
    """Backfill daily logs for a station between two dates with individual daily API calls"""
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Calculate total days
    total_days = (end_dt - start_dt).days + 1
    print(f"Processing {total_days} days from {start_date} to {end_date}")
    print(f"Station ID: {station_id}")
    
    current_date = start_dt
    total_records = 0
    day_count = 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    while current_date <= end_dt:
        day_count += 1
        date_str = current_date.strftime('%Y-%m-%d')
        
        print(f"\nDay {day_count}/{total_days}: {date_str}")
        
        # Create datetime strings for single day API call
        start_str = current_date.strftime('%Y-%m-%d %H:%M:%S')
        end_str = (current_date + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get station history for this single day
        station_data = get_station_history(station_id, start_str, end_str)
        
        day_records = 0
        
        if station_data:
            # Map and insert data
            for data_point in station_data:
                mapped_data = map_api_to_db(data_point)
                
                if mapped_data['timestamp']:
                    cursor.execute('''
                        INSERT OR IGNORE INTO daily_logs 
                        (timestamp, station_id, production_kw, consumption_kw, grid_kw, 
                         battery_kw, soc_percent, pv_kw, generator_kw, grid_tied_inverter_power_kw)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        mapped_data['timestamp'],
                        station_id,
                        mapped_data['production_kw'],
                        mapped_data['consumption_kw'],
                        mapped_data['grid_kw'],
                        mapped_data['battery_kw'],
                        mapped_data['soc_percent'],
                        mapped_data['pv_kw'],
                        mapped_data['generator_kw'],
                        mapped_data['grid_tied_inverter_power_kw']
                    ))
                    day_records += 1
            
            conn.commit()
            print(f"✅ Saved {day_records} frame-level records for {date_str}")
        else:
            print(f"⚠️  No frame-level data received for {date_str}")
        
        total_records += day_records
        current_date += timedelta(days=1)

        # Small delay to avoid rate limiting
        if current_date <= end_dt:
            time.sleep(1)
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Backfill complete: {total_records} records saved from {day_count} days")
    print(f"{'='*60}")
    
    return total_records

def main():
    """Main function to run the backfill"""
    # Parse command line arguments
    if len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    elif len(sys.argv) == 1:
        # Default values if no arguments provided
        start_date = "2025-01-01"
        end_date = "2025-01-31"
    else:
        print("Usage: python3 backfill_daily_logs.py [start_date end_date]")
        print("Example: python3 backfill_daily_logs.py 2024-01-01 2024-12-31")
        print("Default: python3 backfill_daily_logs.py (uses 2025-01-01 to 2025-01-31)")
        return
    
    # Validate date format
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        return
    
    print("Starting daily logs backfill...")
    print(f"Date range: {start_date} to {end_date}")
    
    # Get stations and use first one
    stations = get_station_list()
    if not stations:
        print("No stations found. Please check your API credentials.")
        return
    
    station_id = stations[0].get('id')
    station_name = stations[0].get('sn', f"Station {station_id}")
    
    print(f"Found {len(stations)} stations")
    print(f"Processing station: {station_name} (ID: {station_id})")
    
    # Backfill frame-level data using chunked approach
    total_records = backfill_daily_logs(station_id, start_date, end_date)
    
    if total_records > 0:
        print(f"\n🎉 Successfully backfilled {total_records} frame-level records!")
    else:
        print(f"\n⚠️  No frame-level data was saved. Check API availability or date range.")
    
    print("\nBackfill process completed!")

if __name__ == '__main__':
    main()
