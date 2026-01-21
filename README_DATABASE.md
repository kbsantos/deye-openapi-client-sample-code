# Solar System Database

Automated daily data collection and storage for your Deye solar system.

## Overview

This system automatically collects and stores daily solar data including:
- Generation (kWh)
- Grid Feed-in (kWh)
- Grid Purchase (kWh)
- Battery Charge (kWh)
- Battery Discharge (kWh)
- Consumption (kWh)
- Full Power Hours

## Quick Start

### 1. Setup Database

```bash
cd /Users/kris/Documents/Project/Deye/openApi
python3 db_setup.py
```

This creates `solar_data.db` SQLite database.

### 2. Backfill Historical Data

Load existing data into the database:

```bash
# Load last 7 days
python3 backfill_data.py last7

# Load last 30 days
python3 backfill_data.py last30

# Load specific date range
python3 backfill_data.py 2026-01-01 2026-01-07
```

### 3. View Your Data

```bash
# View last 7 days
python3 view_data.py

# View last 30 days
python3 view_data.py 30

# View monthly summary
python3 view_data.py month 2026 1

# View date range
python3 view_data.py range 2026-01-01 2026-01-31
```

### 4. Setup Daily Updates

Run the daily update script manually:

```bash
python3 daily_update.py
```

This fetches yesterday's data and adds it to the database.

## Automated Daily Updates with Cron

To automatically update the database every day at 6 AM:

### Option 1: Using the setup script (Recommended)

```bash
python3 setup_cron.py
```

### Option 2: Manual cron setup

1. Open crontab editor:
```bash
crontab -e
```

2. Add this line (update path if needed):
```bash
0 6 * * * cd /Users/kris/Documents/Project/Deye/openApi && /Users/kris/Documents/Project/Deye/openApi/venv/bin/python /Users/kris/Documents/Project/Deye/openApi/daily_update.py >> /Users/kris/Documents/Project/Deye/openApi/logs/cron.log 2>&1
```

3. Save and exit (`:wq` in vim)

This runs the update script every day at 6:00 AM and logs output.

## Database Schema

### Table: daily_data
- `id`: Auto-increment primary key
- `date`: Date (YYYY-MM-DD)
- `station_id`: Station ID
- `generation_kwh`: Daily solar generation
- `grid_feedin_kwh`: Energy exported to grid
- `grid_purchase_kwh`: Energy imported from grid
- `battery_charge_kwh`: Battery charging energy
- `battery_discharge_kwh`: Battery discharging energy
- `consumption_kwh`: Total consumption
- `full_power_hours`: Equivalent hours at full capacity
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

### Table: station_info
- `station_id`: Station ID (primary key)
- `station_name`: Station name
- `installed_capacity`: Installed capacity (kW)
- `location_address`: Physical address
- `grid_type`: Grid connection type
- `last_updated`: Last update timestamp

## Scripts Reference

### db_setup.py
Creates the database and tables.

```bash
python3 db_setup.py
```

### daily_update.py
Fetches yesterday's data and updates database.

```bash
python3 daily_update.py
```

### backfill_data.py
Loads historical data for a date range.

```bash
python3 backfill_data.py START_DATE END_DATE
python3 backfill_data.py 2026-01-01 2026-01-31
```

### view_data.py
Query and display stored data.

```bash
# Last 7 days (default)
python3 view_data.py

# Last N days
python3 view_data.py 30

# Monthly summary
python3 view_data.py month 2026 1

# Date range
python3 view_data.py range 2026-01-01 2026-01-31
```

## Data Analysis Examples

### Export to CSV

```python
import sqlite3
import csv

conn = sqlite3.connect('solar_data.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM daily_data ORDER BY date')

with open('solar_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([i[0] for i in cursor.description])
    writer.writerows(cursor.fetchall())

conn.close()
```

### Query with Python

```python
import sqlite3

conn = sqlite3.connect('solar_data.db')
cursor = conn.cursor()

# Get best generation day
cursor.execute('''
    SELECT date, generation_kwh
    FROM daily_data
    ORDER BY generation_kwh DESC
    LIMIT 1
''')

print(cursor.fetchone())
conn.close()
```

## Troubleshooting

### Database not found
Run `python3 db_setup.py` to create it.

### Token expired
Update token in `clientcode/variable.py` by running:
```bash
PYTHONPATH=. venv/bin/python clientcode/account/obtain_token.py
```

### Missing dependencies
```bash
source venv/bin/activate
pip install requests
```

### Cron not running
Check cron is enabled:
```bash
# Check if cron service is running (macOS)
sudo launchctl list | grep cron

# View cron logs
tail -f /Users/kris/Documents/Project/Deye/openApi/logs/cron.log
```

## Files

- `solar_data.db` - SQLite database (created automatically)
- `db_setup.py` - Database setup script
- `daily_update.py` - Daily data collection script
- `backfill_data.py` - Historical data loader
- `view_data.py` - Data viewer
- `setup_cron.py` - Automated cron setup
- `logs/cron.log` - Cron execution log

## Notes

- Data is fetched from DeyeCloud EU API
- API has a limit of 31 days per request
- Database uses SQLite (no server required)
- All timestamps in UTC
- Backfill script adds 1-second delay between requests to avoid rate limiting
