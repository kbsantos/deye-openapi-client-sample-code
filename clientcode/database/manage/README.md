# `clientcode/database/manage` Directory

This directory contains Python scripts essential for the setup, management, and population of the `solar_data.db` SQLite database. These scripts are designed to be run from the project's root directory for proper path resolution.

## Contents

*   ### `db_setup.py`
    This script initializes the `solar_data.db` database. It creates the necessary tables (`daily_data`, `station_info`, `grid_rates`, `daily_logs`) and populates the `grid_rates` table with initial data. It is crucial to run this script before any other database interaction scripts.

    **Tables Created:**
    - `daily_data`: Daily aggregated solar data
    - `station_info`: Station metadata and configuration
    - `grid_rates`: Electricity buy/sell rates by month
    - `daily_logs`: Detailed frame-level solar metrics

    **Usage:**
    ```bash
    python3 clientcode/database/manage/db_setup.py
    ```

*   ### `manage_grid_rates.py`
    This script provides a command-line interface for performing CRUD (Create, Read, Update, Delete) operations on the `grid_rates` table within `solar_data.db`.

    **Usage:**
    *   **View all rates:**
        ```bash
        python3 clientcode/database/manage/manage_grid_rates.py view
        ```
    *   **Add a new rate:**
        ```bash
        python3 clientcode/database/manage/manage_grid_rates.py add <year> <month> <sell_rate> <buy_rate>
        # Example: python3 clientcode/database/manage/manage_grid_rates.py add 2026 1 12.0 5.0
        ```
    *   **Update an existing rate:**
        ```bash
        python3 clientcode/database/manage/manage_grid_rates.py update <id> <year> <month> <sell_rate> <buy_rate>
        # Example: python3 clientcode/database/manage/manage_grid_rates.py update 20 2026 1 12.5 5.5
        ```
    *   **Delete a rate:**
        ```bash
        python3 clientcode/database/manage/manage_grid_rates.py delete <id>
        # Example: python3 clientcode/database/manage/manage_grid_rates.py delete 20
        ```

*   ### `backfill_data.py`
    This script is used to fetch historical solar data from the DeyeCloud API and populate the `daily_data` table in `solar_data.db`. It supports fetching data for specific date ranges or for predefined periods (e.g., last 7 days, last 30 days).

    **Usage:**
    *   **Fetch data for a specific date range:**
        ```bash
        python3 clientcode/database/manage/backfill_data.py <START_DATE> <END_DATE>
        # Example: python3 clientcode/database/manage/backfill_data.py 2024-05-01 2024-05-31
        ```
    *   **Fetch data for the last 7 days:**
        ```bash
        python3 clientcode/database/manage/backfill_data.py last7
        ```
    *   **Fetch data for the last 30 days:**
        ```bash
        python3 clientcode/database/manage/backfill_data.py last30
        ```

*   ### `backfill_daily_logs.py`
    This script fetches detailed frame-level solar data from the DeyeCloud API and populates the `daily_logs` table. It provides granular data including production, consumption, grid power, battery status, and other metrics at frame-level intervals.

    **Features:**
    - Fetches data from station history API with frame-level granularity
    - Maps API fields to database columns:
      - `generationPower` → `production_kw` & `pv_kw`
      - `consumptionPower` → `consumption_kw`
      - `gridPower` → `grid_kw`
      - `batteryPower` → `battery_kw`
      - `batterySOC` → `soc_percent`
      - `wirePower` → `grid_tied_inverter_power_kw`
    - Processes data in 30-day chunks to avoid API limits
    - Includes rate limiting to prevent overwhelming the API
    - Uses `INSERT OR REPLACE` to avoid duplicates

    **Usage:**
    *   **With custom date range:**
        ```bash
        python3 clientcode/database/manage/backfill_daily_logs.py <start_date> <end_date>
        # Example: python3 clientcode/database/manage/backfill_daily_logs.py 2024-01-01 2024-12-31
        ```
    *   **With default date range (2025-01-01 to 2025-01-31):**
        ```bash
        python3 clientcode/database/manage/backfill_daily_logs.py
        ```

    **Configuration:**
    - Dates must be in YYYY-MM-DD format
    - Script processes all stations automatically
    - Processes data in 30-day chunks to avoid API limits

    **Example Output:**
    ```
    Starting daily logs backfill...
    Found 1 stations
    Processing station: Station 61086157 (ID: 61086157)
    Backfilling data for station 61086157 from 2025-01-01 to 2025-01-31
    Fetching data from 2025-01-01 00:00:00 to 2025-01-30 23:59:59
    Inserted 284 records for this chunk
    Fetching data from 2025-01-31 00:00:00 to 2025-01-31 23:59:59
    Inserted 271 records for this chunk
    Backfill completed. Total records inserted: 555
    Successfully backfilled 555 records for Station 61086157
    ```

## Database Schema

### daily_logs Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| timestamp | TIMESTAMP | Time of the log entry |
| station_id | INTEGER | Foreign key to station_info |
| production_kw | REAL | Production in kW |
| consumption_kw | REAL | Consumption in kW |
| grid_kw | REAL | Grid power in kW |
| battery_kw | REAL | Battery power in kW |
| soc_percent | REAL | State of charge percentage |
| pv_kw | REAL | PV power in kW |
| generator_kw | REAL | Generator power in kW |
| grid_tied_inverter_power_kw | REAL | Grid-tied inverter power in kW |
| created_at | TIMESTAMP | Record creation timestamp |

## Prerequisites

1. **API Credentials**: Ensure `clientcode/variable.py` contains valid API credentials
2. **Database Setup**: Run `db_setup.py` before running backfill scripts
3. **Authentication**: Valid token in `clientcode/variable.py` (not expired)

## Important Note

All scripts in this directory are designed to be run from the project's root directory (`/home/kris/Projects/Solar/`) to ensure proper resolution of internal module imports (e.g., `from clientcode import variable`) and database paths.
