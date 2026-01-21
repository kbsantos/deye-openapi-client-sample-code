#!/usr/bin/env python3
"""
Backfill historical data into database
Fetches data for a date range and populates the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import sqlite3
from datetime import datetime, timedelta
import time

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
else:
    print("Error: Could not find project root ('.git' directory).")
    sys.exit(1)

from clientcode import variable

DB_PATH = os.path.join(project_root, 'clientcode', 'database', 'solar_data.db')
STATION_ID = 61086157

def fetch_date_range_data(start_date, end_date):
    """Fetch data for a date range from API"""
    url = variable.baseurl + '/station/history'
    headers = variable.headers

    data = {
        "stationId": STATION_ID,
        "granularity": 2,  # Daily granularity
        "startAt": start_date,
        "endAt": end_date
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get('success') and result.get('stationDataItems'):
            return result['stationDataItems']
        else:
            print(f"Error: {result.get('msg', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def save_batch_to_database(data_items):
    """Save multiple days of data to database"""
    if not data_items:
        return 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    saved_count = 0

    for item in data_items:
        try:
            # Construct date from year, month, day fields
            date_str = f"{item['year']}-{item['month']:02d}-{item['day']:02d}"

            cursor.execute('''
            INSERT OR REPLACE INTO daily_data
            (date, station_id, generation_kwh, grid_feedin_kwh, grid_purchase_kwh,
             battery_charge_kwh, battery_discharge_kwh, consumption_kwh, full_power_hours,
             updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                date_str,
                STATION_ID,
                item.get('generationValue'),
                item.get('gridValue'),
                item.get('purchaseValue'),
                item.get('chargeValue'),
                item.get('dischargeValue'),
                item.get('consumptionValue'),
                item.get('fullPowerHours')
            ))

            saved_count += 1
            print(f"✓ {date_str}: Gen={item.get('generationValue'):.1f} kWh, Consumption={item.get('consumptionValue'):.1f} kWh")

        except Exception as e:
            print(f"✗ Error saving {date_str}: {e}")

    conn.commit()
    conn.close()

    return saved_count

def backfill_date_range(start_date_str, end_date_str):
    """Backfill data for a date range"""
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    if (end_date - start_date).days > 31:
        print("Warning: Date range exceeds 31 days. Processing in chunks...")

    current_start = start_date
    total_saved = 0

    while current_start < end_date:
        # Process in 30-day chunks (API limit is 31 days)
        current_end = min(current_start + timedelta(days=30), end_date)

        print(f"\nFetching data: {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')}")

        data = fetch_date_range_data(
            current_start.strftime('%Y-%m-%d'),
            current_end.strftime('%Y-%m-%d')
        )

        if data:
            saved = save_batch_to_database(data)
            total_saved += saved
            print(f"Saved {saved} days of data")
        else:
            print("No data received")

        current_start = current_end

        # Small delay to avoid rate limiting
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Backfill complete: {total_saved} days saved")
    print(f"{'='*60}")

def main():
    """Main execution"""
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print("Database not found. Creating database...")
        from db_setup import create_database
        create_database()

    if len(sys.argv) < 2:
        print("Usage: python backfill_data.py START_DATE END_DATE")
        print("Example: python backfill_data.py 2026-01-01 2026-01-07")
        print("\nOr use quick options:")
        print("  python backfill_data.py last7   # Last 7 days")
        print("  python backfill_data.py last30  # Last 30 days")
        return 1

    arg1 = sys.argv[1]

    # Handle quick options
    if arg1 == 'last7':
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
    elif arg1 == 'last30':
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
    else:
        # Regular date range mode
        if len(sys.argv) != 3:
            print("Error: Date range mode requires two dates")
            print("Usage: python backfill_data.py START_DATE END_DATE")
            return 1
        start_date_str = arg1
        end_date_str = sys.argv[2]

    # Validate date format
    try:
        datetime.strptime(start_date_str, '%Y-%m-%d')
        datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD")
        return 1

    backfill_date_range(start_date_str, end_date_str)
    return 0

if __name__ == '__main__':
    sys.exit(main())
