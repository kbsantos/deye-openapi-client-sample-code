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

def get_summary_by_month(): 
  if not os.path.exists(DB_PATH):
    print("Database not found. Run db_setup.py first.")
    return

  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  query = """
    SELECT
        t.billing_month                                                                 AS Month,
        printf('%05.2f', ROUND(gr.sell_rate_kwh, 2))                                    AS sell,
        printf('%05.2f', ROUND(gr.buy_rate_kwh, 2))                                     AS buy,
        printf('%07.2f', ROUND(SUM(t.grid_purchase_kwh), 2))                            AS purchase,
        printf('%08.2f', ROUND((SUM(t.grid_purchase_kwh) *  gr.sell_rate_kwh), 2))      AS purchase_rate,
        printf('%07.2f', ROUND(SUM(t.generated), 2))                                    AS generated,
        printf('%08.2f', ROUND((SUM(t.generated) * gr.sell_rate_kwh), 2))               AS generated_rate,
        printf('%07.2f', ROUND(SUM(t.grid_feedin_kwh), 2) )                             AS feedin,
        printf('%08.2f', ROUND((SUM(t.grid_feedin_kwh) * gr.buy_rate_kwh), 2))          AS feedin_rate
    FROM (
        SELECT
            strftime('%Y-%m', DATE(date, '-25 days')) AS billing_month,
            strftime('%Y',   DATE(date, '-25 days')) AS rate_year,
            strftime('%m',   DATE(date, '-25 days')) AS rate_month,
            generation_kwh,
            grid_feedin_kwh,
            grid_purchase_kwh,
            battery_charge_kwh,
            battery_discharge_kwh,
            (generation_kwh + battery_charge_kwh + battery_discharge_kwh) as generated
        FROM daily_data
    ) t
    LEFT JOIN grid_rates gr
        ON gr.year  = CAST(t.rate_year AS INTEGER)
      AND gr.month = CAST(t.rate_month AS INTEGER)
    GROUP BY
        t.billing_month,
        t.rate_year,
        t.rate_month,
        gr.sell_rate_kwh,
        gr.buy_rate_kwh
    ORDER BY t.billing_month;
  """
  cursor.execute(query)
  rows = cursor.fetchall()
  columns = [description[0] for description in cursor.description]
  conn.close()

  if not rows:
    print("No data found in database.")
    return

  print(f"\n{'='*120}")
  print(f"Summary per Month")
  print(f"{'='*120}\n")
  print_results(columns, rows)
   
def get_summary_by_year(): 
  if not os.path.exists(DB_PATH):
    print("Database not found. Run db_setup.py first.")
    return

  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  query = """
      SELECT
          t.billing_year AS year,
          printf('%08.2f', ROUND(SUM(t.grid_purchase_kwh), 2)) AS purchase,
          printf('%09.2f', ROUND(SUM(t.grid_purchase_kwh * gr.sell_rate_kwh), 2)) AS purchase_rate,
          printf('%08.2f', ROUND(SUM(t.generated), 2)) AS generated,
          printf('%09.2f', ROUND(SUM(t.generated * gr.sell_rate_kwh), 2)) AS generated_rate,
          printf('%08.2f', ROUND(SUM(t.grid_feedin_kwh), 2)) AS feedin,
          printf('%09.2f', ROUND(SUM(t.grid_feedin_kwh * gr.buy_rate_kwh), 2)) AS feedin_rate

      FROM (
          SELECT
              strftime('%Y', DATE(date, '-25 days')) AS billing_year,
              strftime('%Y', DATE(date, '-25 days')) AS rate_year,
              strftime('%m', DATE(date, '-25 days')) AS rate_month,

              generation_kwh,
              grid_feedin_kwh,
              grid_purchase_kwh,
              battery_charge_kwh,
              battery_discharge_kwh,

              (generation_kwh + battery_charge_kwh + battery_discharge_kwh) AS generated
          FROM daily_data
      ) t
      LEFT JOIN grid_rates gr
        ON gr.year  = CAST(t.rate_year AS INTEGER)
      AND gr.month = CAST(t.rate_month AS INTEGER)

      GROUP BY t.billing_year
      ORDER BY t.billing_year
    """
  cursor.execute(query)
  rows = cursor.fetchall()
  columns = [description[0] for description in cursor.description]
  conn.close()

  if not rows:
    print("No data found in database.")
    return

  print(f"\n{'='*120}")
  print(f"Summary per Year")
  print(f"{'='*120}")
  print_results(columns, rows)
   
def get_summary_by_roi(): 
  if not os.path.exists(DB_PATH):
    print("Database not found. Run db_setup.py first.")
    return

  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  query = """
    SELECT
      CAST(running_months AS INTEGER)               AS running_month,
      CAST(kwhpm AS INTEGER)                        AS ave_kwh_month,
      CAST(apm AS INTEGER)                          AS ave_rate_month,
      CAST(generated_kwh AS INTEGER)                AS total_kwh,
      CAST(generated_rate AS INTEGER)               AS total_rate,
      750000                                        AS investments,
      ROUND((750000 - generated_rate), 2)           AS remaining_roi,
      ROUND(((750000 - generated_rate) / apm) , 2)  AS remaining_month_roi
    FROM 
      (SELECT 
          printf('%09.2f', ROUND(SUM(t.generated) + SUM(t.grid_feedin_kwh), 2)) AS generated_kwh,
          printf('%10.2f', ROUND((SUM(t.generated * gr.sell_rate_kwh) + SUM(t.grid_feedin_kwh * gr.buy_rate_kwh)), 2)) AS generated_rate,
          COUNT(DISTINCT t.billing_year || '-' || t.rate_month) AS running_months,
          ROUND(((SUM(t.generated * gr.sell_rate_kwh) + SUM(t.grid_feedin_kwh * gr.buy_rate_kwh)) /  COUNT(DISTINCT t.billing_year || '-' || t.rate_month)), 2) AS apm,
          ROUND(((SUM(t.generated) + SUM(t.grid_feedin_kwh)) /  COUNT(DISTINCT t.billing_year || '-' || t.rate_month)), 2) AS kwhpm

        FROM (
            SELECT
                strftime('%Y', DATE(date, '-25 days')) AS billing_year,
                strftime('%m', DATE(date, '-25 days')) AS rate_month,
                generation_kwh,
                grid_feedin_kwh,
                battery_charge_kwh,
                battery_discharge_kwh,

                (generation_kwh + battery_charge_kwh + battery_discharge_kwh) AS generated
            FROM daily_data
        ) t
        LEFT JOIN grid_rates gr
          ON gr.year  = CAST(t.billing_year AS INTEGER)
        AND gr.month = CAST(t.rate_month AS INTEGER)
      ) tot ;
    """
  cursor.execute(query)
  row = cursor.fetchone()
  conn.close()

  if not row:
    print("No data found in database.")
    return

  running_month, ave_kwh_month, ave_rate_month, total_kwh, total_rate, investments, remaining_roi, remaining_month_roi = row

  print(f"\n{'='*120}")
  print(f"Summary ROI")
  print(f"{'='*120}\n")
  print(f"Investment: {investments}\n")

  print(f"Return Of Investment:")
  print(f"  Remaining: {remaining_roi:.1f} peso")
  print(f"  Remaining Months: {remaining_month_roi:.1f}")
  
  print(f"\nGeneration:")
  print(f"  Total: {total_kwh:.1f} kWh")
  print(f"  Total Rate: {total_rate:.1f} peso")
  print(f"  Average: {ave_kwh_month:.1f} kWh/m")
  print(f"  Average Rate: {ave_rate_month:.1f} peso/m\n")
  print(f"{'*'*120}\n")
 
  
def print_results(columns, results):
    """Print query results in a formatted table"""
    if not results:
        print("No results found.")
        return

    # Print header
    print(" | ".join(columns))
    print("-" * 120)

    # Print rows
    for row in results:
        print(" | ".join(str(val) for val in row))
    print()

    print(f"{'*'*120}\n")

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

def get_date_range_summary(start_date, end_date):
    """Get summary for specific date range"""
    if not os.path.exists(DB_PATH):
        print("Database not found. Run db_setup.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
    WHERE date BETWEEN ? AND ?
    ''', (start_date, end_date))

    row = cursor.fetchone()
    conn.close()

    if row[0] == 0:
        print(f"No data found between {start_date} and {end_date}")
        return

    days, total_gen, total_feedin, total_purchase, total_charge, total_discharge, total_consumption, avg_gen, max_gen, min_gen = row

    print(f"\n{'='*60}")
    print(f"Date Range Summary: {start_date} to {end_date}")
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
        elif command == 'summary' and len(sys.argv) == 4:
            start = sys.argv[2]
            end = sys.argv[3]
            get_date_range_summary(start, end)
        elif command == 'all':
            get_summary_by_roi()
            get_summary_by_year()
            get_summary_by_month()
        elif command.isdigit():
            days = int(command)
            get_recent_data(days)
        else:
            print("Usage:")
            print("  python summary_data.py                         # View last 7 days")
            print("  python summary_data.py 30                      # View last 30 days")
            print("  python summary_data.py all                     # All Summaries")
            print("  python summary_data.py month 2026 1            # Monthly summary")
            print("  python summary_data.py range 2026-01-01 2026-01-31    # Date range data")
            print("  python summary_data.py summary 2026-01-01 2026-01-31  # Date range summary")
    else:
        get_recent_data(7)

if __name__ == '__main__':
    main()
