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
STATION_ID = 61086157

def get_yesterday_date():
    """Get yesterday's date in YYYY-MM-DD format"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')

def fetch_daily_data(date):
    """Fetch daily data from API for specified date"""
    url = variable.baseurl + '/station/history'
    headers = variable.headers

    # Request data for single day
    data = {
        "stationId": STATION_ID,
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

def save_to_database(date, data):
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
            STATION_ID,
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

    # Get yesterday's date
    yesterday = get_yesterday_date()
    print(f"Fetching data for: {yesterday}")

    # Update station info
    update_station_info()

    # Fetch and save data
    data = fetch_daily_data(yesterday)
    if data:
        success = save_to_database(yesterday, data)
        if success:
            print("\n✓ Daily update completed successfully!")
            return 0
        else:
            print("\n✗ Failed to save data")
            return 1
    else:
        print("\n✗ Failed to fetch data")
        return 1

if __name__ == '__main__':
    sys.exit(main())
