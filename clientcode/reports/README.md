# Solar Data Reports

This directory contains reporting and analysis tools for solar system data.

## frame_summary.py

A comprehensive tool for analyzing frame-level solar data from the `daily_logs` table.

### Features

- **Single Date Analysis**: Analyze frame data for a specific day
- **Date Range Analysis**: Get summary statistics across multiple days
- **Available Dates**: View all dates with frame data in the database
- **Flexible Filtering**: Filter by station ID and limit results
- **Detailed Metrics**: Production, consumption, grid, battery, SOC, PV, and inverter power

### Usage Examples

```bash
# Show available dates with data
python3 frame_summary.py --dates

# Analyze specific date
python3 frame_summary.py --date 2025-01-15

# Analyze date range
python3 frame_summary.py --start 2025-01-01 --end 2025-01-07

# Limit number of frames displayed
python3 frame_summary.py --date 2025-01-15 --limit 50

# Filter by station ID
python3 frame_summary.py --date 2025-01-15 --station 61086157

# Show help
python3 frame_summary.py --help
```

### Output Information

The tool provides two types of output:

1. **Summary Statistics**:
   - Total number of frames
   - First and last record timestamps
   - Average and maximum values for each metric
   - Battery SOC statistics

2. **Frame-Level Details**:
   - Individual frame records with timestamps
   - Power values in kilowatts (kW)
   - Battery state of charge percentage
   - Grid-tied inverter power

### Data Metrics

- **Production (kW)**: Solar panel power generation
- **Consumption (kW)**: Total power consumption
- **Grid Power (kW)**: Power flow to/from grid (positive = export, negative = import)
- **Battery Power (kW)**: Battery charging/discharging (positive = charging, negative = discharging)
- **SOC (%)**: Battery state of charge percentage
- **PV (kW)**: Photovoltaic panel power output
- **Inverter (kW)**: Grid-tied inverter power output

### Database Requirements

The tool requires:
- SQLite database at `clientcode/database/solar_data.db`
- `daily_logs` table with frame-level data
- Proper database permissions for read access

### Dependencies

- Python 3.6+
- sqlite3 (standard library)
- datetime (standard library)
- argparse (standard library)

### Notes

- Frame data is captured at 5-minute intervals
- Negative grid power indicates power import from grid
- Negative battery power indicates battery discharge
- Data is sourced from the daily cron job updates
- Historical data can be backfilled using `backfill_daily_logs.py`
