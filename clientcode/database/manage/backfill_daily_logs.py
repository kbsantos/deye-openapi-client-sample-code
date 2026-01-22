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
    """Map API response fields to database fields"""
    return {
        'timestamp': convert_timestamp(station_data.get('timeStamp')),
        'production_kw': station_data.get('generationPower'),
        'consumption_kw': station_data.get('consumptionPower'),
        'grid_kw': station_data.get('gridPower'),
        'battery_kw': station_data.get('batteryPower'),
        'soc_percent': station_data.get('batterySOC'),
        'pv_kw': station_data.get('generationPower'),  # Using generationPower as PV power
        'generator_kw': None,  # Not available in API response
        'grid_tied_inverter_power_kw': station_data.get('wirePower')
    }

def backfill_daily_logs(station_id, start_date, end_date):
    """Backfill daily logs for a station between two dates"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Convert dates to timestamps for API
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) + 86400  # Add one day
    
    print(f"Backfilling data for station {station_id} from {start_date} to {end_date}")
    
    # Get data in monthly chunks to avoid API limits
    current_start = start_timestamp
    chunk_days = 30  # Process 30 days at a time
    
    records_inserted = 0
    
    while current_start < end_timestamp:
        chunk_end = min(current_start + (chunk_days * 86400), end_timestamp)
        
        # Convert timestamps to strings for API
        start_str = datetime.fromtimestamp(current_start).strftime('%Y-%m-%d %H:%M:%S')
        end_str = datetime.fromtimestamp(chunk_end - 1).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Fetching data from {start_str} to {end_str}")
        
        # Get station history
        station_data = get_station_history(station_id, start_str, end_str)
        
        if station_data:
            # Map and insert data
            for data_point in station_data:
                mapped_data = map_api_to_db(data_point)
                
                if mapped_data['timestamp']:
                    cursor.execute('''
                        INSERT OR REPLACE INTO daily_logs 
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
                    records_inserted += 1
            
            conn.commit()
            print(f"Inserted {len(station_data)} records for this chunk")
        
        current_start = chunk_end
        
        # Rate limiting to avoid overwhelming the API
        time.sleep(1)
    
    conn.close()
    print(f"Backfill completed. Total records inserted: {records_inserted}")
    return records_inserted

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
    
    # Get stations
    stations = get_station_list()
    if not stations:
        print("No stations found. Please check your API credentials.")
        return
    
    print(f"Found {len(stations)} stations")
    
    # Backfill for each station
    for station in stations:
        station_id = station.get('id')
        station_name = station.get('sn', f"Station {station_id}")
        
        print(f"\nProcessing station: {station_name} (ID: {station_id})")
        
        try:
            records = backfill_daily_logs(station_id, start_date, end_date)
            print(f"Successfully backfilled {records} records for {station_name}")
        except Exception as e:
            print(f"Error backfilling station {station_name}: {e}")
            continue
    
    print("\nBackfill process completed!")

if __name__ == '__main__':
    main()
