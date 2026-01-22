#!/usr/bin/env python3
"""
Daily update script for solar system data
Fetches yesterday's data from DeyeCloud API and stores in database
Run this script daily via cron to keep database updated
"""

import sys
import os

# Function to find the project root (where .git is located)
def find_project_root(current_dir):
    while current_dir != os.path.abspath(os.sep):
        if os.path.exists(os.path.join(current_dir, '.git')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return None

# Get the directory where the script is located
script_dir = os.path.dirname(__file__)
project_root = find_project_root(script_dir)

if project_root:
    sys.path.insert(0, project_root)
    DB_PATH = os.path.join(project_root, 'clientcode', 'database', 'solar_data.db')
else:
    print("Error: Could not find project root ('.git' directory).")
    sys.exit(1)

import requests
import sqlite3
from datetime import datetime, timedelta
from clientcode import variable

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

def get_yesterday_date():
    """Get yesterday's date in YYYY-MM-DD format"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')

def fetch_daily_data(date, station_id):
    """Fetch daily data from API for specified date"""
    url = variable.baseurl + '/station/history'
    headers = variable.headers

    # Request data for single day
    data = {
        "stationId": station_id,
        "granularity": 2,  # Daily granularity
        "startAt": date,
        "endAt": (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get('success') and result.get('stationDataItems'):
            return result['stationDataItems'][0]
        else:
            print(f"Error: {result.get('msg', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_to_database(date, data, station_id):
    """Save daily data to database"""
    if not data:
        print("No data to save")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Insert or replace data
        cursor.execute('''
        INSERT OR REPLACE INTO daily_data
        (date, station_id, generation_kwh, grid_feedin_kwh, grid_purchase_kwh,
         battery_charge_kwh, battery_discharge_kwh, consumption_kwh, full_power_hours,
         updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            date,
            station_id,
            data.get('generationValue'),
            data.get('gridValue'),
            data.get('purchaseValue'),
            data.get('chargeValue'),
            data.get('dischargeValue'),
            data.get('consumptionValue'),
            data.get('fullPowerHours')
        ))

        conn.commit()
        print(f"✓ Data saved for {date}")
        print(f"  Generation: {data.get('generationValue')} kWh")
        print(f"  Grid Feed-in: {data.get('gridValue')} kWh")
        print(f"  Grid Purchase: {data.get('purchaseValue')} kWh")
        print(f"  Battery Charge: {data.get('chargeValue')} kWh")
        print(f"  Battery Discharge: {data.get('dischargeValue')} kWh")
        print(f"  Consumption: {data.get('consumptionValue')} kWh")
        return True
    except Exception as e:
        print(f"Error saving to database: {e}")
        return False
    finally:
        conn.close()

def get_station_history(station_id, start_time, end_time):
    """Get station history data with frame-level granularity"""
    url = variable.baseurl + '/station/history'
    headers = variable.headers
    data = {
        "stationId": station_id,
        "granularity": 1,  # Frame-level granularity
        "startAt": start_time.split()[0],  # Use only date part
        "endAt": end_time.split()[0]      # Use only date part
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
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

def save_daily_logs(date, station_id):
    """Save frame-level data to daily_logs table"""
    # Get data for yesterday with frame-level granularity
    start_time = f"{date} 00:00:00"
    end_time = f"{date} 23:59:59"
    
    print(f"Fetching frame-level data for {date}...")
    station_data = get_station_history(station_id, start_time, end_time)
    
    if not station_data:
        print(f"No frame-level data found for {date}")
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    records_inserted = 0
    
    try:
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
        print(f"✓ Saved {records_inserted} frame-level records for {date}")
        return records_inserted
        
    except Exception as e:
        print(f"Error saving daily logs: {e}")
        return 0
    finally:
        conn.close()

def update_station_info():
    """Update station information in database"""
    url = variable.baseurl + '/station/list'
    headers = variable.headers
    data = {"page": 1, "size": 10}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get('success') and result.get('stationList'):
            station = result['stationList'][0]

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute('''
            INSERT OR REPLACE INTO station_info
            (station_id, station_name, installed_capacity, location_address,
             grid_type, last_updated)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                station['id'],
                station['name'],
                station['installedCapacity'],
                station['locationAddress'],
                station['gridInterconnectionType']
            ))

            conn.commit()
            conn.close()
            print(f"✓ Station info updated: {station['name']}")
    except Exception as e:
        print(f"Warning: Could not update station info: {e}")

def main():
    """Main execution function"""
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print("Database not found. Creating database...")
        from db_setup import create_database
        create_database()

    # Get stations and use first one
    stations = get_station_list()
    if not stations:
        print("No stations found. Please check your API credentials.")
        return 1
    
    station_id = stations[0].get('id')
    station_name = stations[0].get('sn', f"Station {station_id}")
    
    print(f"Using station: {station_name} (ID: {station_id})")

    # Get yesterday's date
    yesterday = get_yesterday_date()
    print(f"Fetching data for: {yesterday}")

    # Update station info
    update_station_info()

    # Fetch and save data
    data = fetch_daily_data(yesterday, station_id)
    if data:
        success = save_to_database(yesterday, data, station_id)
        if success:
            print("✓ Daily data saved successfully!")
        else:
            print("✗ Failed to save daily data")
    
    # Also save frame-level data to daily_logs table
    daily_logs_count = save_daily_logs(yesterday, station_id)
    if daily_logs_count > 0:
        print(f"✓ Frame-level data saved: {daily_logs_count} records")
    else:
        print("⚠ No frame-level data available")
    
    # Check if at least one operation succeeded
    if (data and success) or (daily_logs_count > 0):
        print("\n✓ Daily update completed successfully!")
        return 0
    else:
        print("\n✗ Failed to fetch or save any data")
        return 1

if __name__ == '__main__':
    sys.exit(main())
