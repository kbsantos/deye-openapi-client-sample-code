# `clientcode/database/manage` Directory

This directory contains Python scripts essential for the setup, management, and population of the `solar_data.db` SQLite database. These scripts are designed to be run from the project's root directory for proper path resolution.

## Contents

*   ### `db_setup.py`
    This script initializes the `solar_data.db` database. It creates the necessary tables (`daily_data`, `station_info`, `grid_rates`) and populates the `grid_rates` table with initial data. It is crucial to run this script before any other database interaction scripts.

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

## Important Note

All scripts in this directory are designed to be run from the project's root directory (`/home/kris/Projects/Solar/`) to ensure proper resolution of internal module imports (e.g., `from clientcode import variable`) and database paths.
