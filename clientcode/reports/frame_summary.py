#!/usr/bin/env python3
"""
Frame Summary Report Generator
Analyzes and displays detailed metrics from daily_logs table
Provides frame-level solar data analysis and summaries
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta
import argparse

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

def get_frame_data(date=None, station_id=None, limit=None):
    """Retrieve frame data from daily_logs table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT timestamp, station_id, production_kw, consumption_kw, grid_kw,
               battery_kw, soc_percent, pv_kw, generator_kw, grid_tied_inverter_power_kw
        FROM daily_logs
        WHERE 1=1
    '''
    params = []
    
    if date:
        query += ' AND DATE(timestamp) = ?'
        params.append(date)
    
    if station_id:
        query += ' AND station_id = ?'
        params.append(station_id)
    
    query += ' ORDER BY timestamp DESC'
    
    if limit:
        query += ' LIMIT ?'
        params.append(limit)
    
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving frame data: {e}")
        return []
    finally:
        conn.close()

def get_date_range_summary(start_date, end_date, station_id=None):
    """Get summary statistics for a date range"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            COUNT(*) as total_frames,
            MIN(timestamp) as first_record,
            MAX(timestamp) as last_record,
            ROUND(AVG(production_kw), 2) as avg_production_kw,
            ROUND(MAX(production_kw), 2) as max_production_kw,
            ROUND(AVG(consumption_kw), 2) as avg_consumption_kw,
            ROUND(MAX(consumption_kw), 2) as max_consumption_kw,
            ROUND(AVG(grid_kw), 2) as avg_grid_kw,
            ROUND(AVG(battery_kw), 2) as avg_battery_kw,
            ROUND(AVG(soc_percent), 1) as avg_soc_percent,
            ROUND(MAX(soc_percent), 1) as max_soc_percent
        FROM daily_logs
        WHERE DATE(timestamp) BETWEEN ? AND ?
    '''
    params = [start_date, end_date]
    
    if station_id:
        query += ' AND station_id = ?'
        params.append(station_id)
    
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting summary: {e}")
        return None
    finally:
        conn.close()

def display_frame_summary(frames, title="Frame Data Summary"):
    """Display frame data in a formatted table"""
    if not frames:
        print("No frame data found.")
        return
    
    print(f"\n{title}")
    print("=" * 120)
    print(f"{'Timestamp':<20} {'Station ID':<12} {'Prod(kW)':<10} {'Cons(kW)':<10} {'Grid(kW)':<10} {'Batt(kW)':<10} {'SOC(%)':<8} {'PV(kW)':<10} {'Inv(kW)':<10}")
    print("-" * 120)
    
    for frame in frames:
        timestamp, station_id, production_kw, consumption_kw, grid_kw, battery_kw, soc_percent, pv_kw, generator_kw, inverter_kw = frame
        
        prod_val = production_kw if production_kw is not None else 0
        cons_val = consumption_kw if consumption_kw is not None else 0
        grid_val = grid_kw if grid_kw is not None else 0
        batt_val = battery_kw if battery_kw is not None else 0
        soc_val = soc_percent if soc_percent is not None else 0
        pv_val = pv_kw if pv_kw is not None else 0
        inv_val = inverter_kw if inverter_kw is not None else 0
        
        print(f"{timestamp or 'N/A':<20} {station_id or 'N/A':<12} "
              f"{prod_val:<10.2f} {cons_val:<10.2f} "
              f"{grid_val:<10.2f} {batt_val:<10.2f} "
              f"{soc_val:<8.1f} {pv_val:<10.2f} {inv_val:<10.2f}")

def display_date_range_summary(summary, start_date, end_date):
    """Display summary statistics for date range"""
    if not summary:
        print("No summary data available.")
        return
    
    total_frames, first_record, last_record, avg_prod, max_prod, avg_cons, max_cons, avg_grid, avg_batt, avg_soc, max_soc = summary
    
    print(f"\nDate Range Summary: {start_date} to {end_date}")
    print("=" * 80)
    print(f"Total Frames:      {total_frames:,}")
    print(f"First Record:      {first_record}")
    print(f"Last Record:       {last_record}")
    print(f"")
    print(f"Production (kW):")
    print(f"  Average:         {avg_prod:>8.2f}")
    print(f"  Maximum:         {max_prod:>8.2f}")
    print(f"")
    print(f"Consumption (kW):")
    print(f"  Average:         {avg_cons:>8.2f}")
    print(f"  Maximum:         {max_cons:>8.2f}")
    print(f"")
    print(f"Grid Power (kW):   {avg_grid:>8.2f}")
    print(f"Battery Power (kW): {avg_batt:>8.2f}")
    print(f"")
    print(f"Battery SOC (%):")
    print(f"  Average:         {avg_soc:>8.1f}")
    print(f"  Maximum:         {max_soc:>8.1f}")

def get_available_dates():
    """Get list of dates with available frame data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT DISTINCT DATE(timestamp) as date, COUNT(*) as frame_count
            FROM daily_logs
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting available dates: {e}")
        return []
    finally:
        conn.close()

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Frame Summary Report Generator')
    parser.add_argument('--date', '-d', help='Specific date to analyze (YYYY-MM-DD)')
    parser.add_argument('--start', '-s', help='Start date for range analysis (YYYY-MM-DD)')
    parser.add_argument('--end', '-e', help='End date for range analysis (YYYY-MM-DD)')
    parser.add_argument('--station', help='Station ID to filter')
    parser.add_argument('--limit', '-l', type=int, help='Limit number of frames to display')
    parser.add_argument('--dates', action='store_true', help='Show available dates with data')
    
    args = parser.parse_args()
    
    print("Frame Summary Report Generator")
    print("=" * 50)
    
    # Show available dates
    if args.dates:
        dates = get_available_dates()
        if dates:
            print(f"\nAvailable Dates with Frame Data:")
            print("-" * 40)
            for date, count in dates:
                print(f"{date}: {count:,} frames")
        else:
            print("No frame data found in database.")
        return
    
    # Date range analysis
    if args.start and args.end:
        summary = get_date_range_summary(args.start, args.end, args.station)
        display_date_range_summary(summary, args.start, args.end)
        
        # Also show some sample frames
        frames = get_frame_data(date=args.start, station_id=args.station, limit=20)
        display_frame_summary(frames, f"Sample Frames for {args.start}")
        return
    
    # Single date analysis
    target_date = args.date or (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get summary for the date
    summary = get_date_range_summary(target_date, target_date, args.station)
    display_date_range_summary(summary, target_date, target_date)
    
    # Get frame details
    frames = get_frame_data(date=target_date, station_id=args.station, limit=args.limit)
    display_frame_summary(frames, f"Frame Data for {target_date}")
    
    # Show usage examples
    if not any([args.date, args.start, args.dates]):
        print(f"\nUsage Examples:")
        print(f"  Show available dates:    python3 frame_summary.py --dates")
        print(f"  Analyze specific date:  python3 frame_summary.py --date 2025-01-15")
        print(f"  Date range analysis:    python3 frame_summary.py --start 2025-01-01 --end 2025-01-07")
        print(f"  Limit results:          python3 frame_summary.py --date 2025-01-15 --limit 50")
        print(f"  Filter by station:      python3 frame_summary.py --date 2025-01-15 --station 61086157")

if __name__ == '__main__':
    main()
