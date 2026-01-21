#!/usr/bin/env python3
"""
View solar system data from database
Query and display stored historical data
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta

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

def get_recent_data(days=7):
    """Get recent data for specified number of days"""
    if not os.path.exists(DB_PATH):
        print("Database not found. Run db_setup.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT date, generation_kwh, grid_feedin_kwh, grid_purchase_kwh,
           battery_charge_kwh, battery_discharge_kwh, consumption_kwh,
           full_power_hours
    FROM daily_data
    ORDER BY date DESC
    LIMIT ?
    ''', (days,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No data found in database.")
        return

    # Display header
    print("\n" + "="*120)
    print(f"Solar System Daily Data - Last {days} Days")
    print("="*120)
    print(f"{'Date':<12} {'Gen':<8} {'Feed-in':<9} {'Purchase':<9} {'Charge':<8} {'Discharge':<10} {'Consump':<9} {'FPH':<6}")
    print(f"{'':12} {'(kWh)':<8} {'(kWh)':<9} {'(kWh)':<9} {'(kWh)':<8} {'(kWh)':<10} {'(kWh)':<9} {'(hrs)':<6}")
    print("-"*120)

    # Display data
    total_gen = 0
    total_feedin = 0
    total_purchase = 0
    total_charge = 0
    total_discharge = 0
    total_consumption = 0

    for row in reversed(rows):  # Show oldest first
        date, gen, feedin, purchase, charge, discharge, consumption, fph = row
        print(f"{date:<12} {gen:>7.1f} {feedin:>8.1f} {purchase:>8.1f} {charge:>7.1f} {discharge:>9.1f} {consumption:>8.1f} {fph:>5.2f}")

        total_gen += gen or 0
        total_feedin += feedin or 0
        total_purchase += purchase or 0
        total_charge += charge or 0
        total_discharge += discharge or 0
        total_consumption += consumption or 0

    # Display totals
    print("-"*120)
    print(f"{'TOTAL':<12} {total_gen:>7.1f} {total_feedin:>8.1f} {total_purchase:>8.1f} {total_charge:>7.1f} {total_discharge:>9.1f} {total_consumption:>8.1f}")
    print(f"{'AVERAGE':<12} {total_gen/days:>7.1f} {total_feedin/days:>8.1f} {total_purchase/days:>8.1f} {total_charge/days:>7.1f} {total_discharge/days:>9.1f} {total_consumption/days:>8.1f}")
    print("="*120)

    # Calculate statistics
    self_sufficiency = (total_gen / total_consumption * 100) if total_consumption > 0 else 0
    grid_dependence = (total_purchase / total_consumption * 100) if total_consumption > 0 else 0

    print(f"\nSelf-Sufficiency: {self_sufficiency:.1f}%")
    print(f"Grid Dependence: {grid_dependence:.1f}%")
    print(f"Net Grid Balance: {total_feedin - total_purchase:+.1f} kWh")
    print()

def get_date_range_data(start_date, end_date):
    """Get data for specific date range"""
    if not os.path.exists(DB_PATH):
        print("Database not found. Run db_setup.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT date, generation_kwh, grid_feedin_kwh, grid_purchase_kwh,
           battery_charge_kwh, battery_discharge_kwh, consumption_kwh
    FROM daily_data
    WHERE date BETWEEN ? AND ?
    ORDER BY date
    ''', (start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No data found between {start_date} and {end_date}")
        return

    print(f"\nData from {start_date} to {end_date}:")
    print("-" * 100)
    for row in rows:
        date, gen, feedin, purchase, charge, discharge, consumption = row
        print(f"{date}: Gen={gen:.1f} kWh, Consumption={consumption:.1f} kWh, Purchase={purchase:.1f} kWh")

def get_monthly_summary(year, month):
    """Get monthly summary"""
    if not os.path.exists(DB_PATH):
        print("Database not found. Run db_setup.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    month_str = f"{year}-{month:02d}"

    cursor.execute('''
    SELECT
        COUNT(*) as days,
        SUM(generation_kwh) as total_gen,
        SUM(grid_feedin_kwh) as total_feedin,
        SUM(grid_purchase_kwh) as total_purchase,
        SUM(battery_charge_kwh) as total_charge,
        SUM(battery_discharge_kwh) as total_discharge,
        SUM(consumption_kwh) as total_consumption,
        AVG(generation_kwh) as avg_gen,
        MAX(generation_kwh) as max_gen,
        MIN(generation_kwh) as min_gen
    FROM daily_data
    WHERE date LIKE ?
    ''', (f"{month_str}%",))

    row = cursor.fetchone()
    conn.close()

    if row[0] == 0:
        print(f"No data found for {month_str}")
        return

    days, total_gen, total_feedin, total_purchase, total_charge, total_discharge, total_consumption, avg_gen, max_gen, min_gen = row

    print(f"\n{'='*60}")
    print(f"Monthly Summary: {month_str}")
    print(f"{'='*60}")
    print(f"Days recorded: {days}")
    print(f"\nGeneration:")
    print(f"  Total: {total_gen:.1f} kWh")
    print(f"  Average: {avg_gen:.1f} kWh/day")
    print(f"  Best day: {max_gen:.1f} kWh")
    print(f"  Worst day: {min_gen:.1f} kWh")
    print(f"\nConsumption:")
    print(f"  Total: {total_consumption:.1f} kWh")
    print(f"  Average: {total_consumption/days:.1f} kWh/day")
    print(f"\nGrid:")
    print(f"  Feed-in: {total_feedin:.1f} kWh")
    print(f"  Purchase: {total_purchase:.1f} kWh")
    print(f"  Net: {total_feedin - total_purchase:+.1f} kWh")
    print(f"\nBattery:")
    print(f"  Charge: {total_charge:.1f} kWh")
    print(f"  Discharge: {total_discharge:.1f} kWh")
    print(f"  Net: {total_charge - total_discharge:+.1f} kWh")

    self_sufficiency = (total_gen / total_consumption * 100) if total_consumption > 0 else 0
    print(f"\nSelf-Sufficiency: {self_sufficiency:.1f}%")
    print(f"{'='*60}\n")

def main():
    """Main execution"""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'month' and len(sys.argv) == 4:
            year = int(sys.argv[2])
            month = int(sys.argv[3])
            get_monthly_summary(year, month)
        elif command == 'range' and len(sys.argv) == 4:
            start = sys.argv[2]
            end = sys.argv[3]
            get_date_range_data(start, end)
        elif command.isdigit():
            days = int(command)
            get_recent_data(days)
        else:
            print("Usage:")
            print("  python view_data.py              # View last 7 days")
            print("  python view_data.py 30           # View last 30 days")
            print("  python view_data.py month 2026 1 # Monthly summary")
            print("  python view_data.py range 2026-01-01 2026-01-31")
    else:
        get_recent_data(7)

if __name__ == '__main__':
    main()
