# GEMINI.md

## Project Overview

This project is a Python-based tool for interacting with the DeyeCloud API to monitor and control a solar energy system. It allows users to fetch data from their solar installation, store it in a local SQLite database, and generate reports. The project also includes scripts for controlling the solar energy system, such as setting the battery mode and updating system parameters.

The project is structured into several directories:
- `clientcode/account`: Scripts for managing API credentials and obtaining access tokens.
- `clientcode/commission`: Scripts for controlling the solar energy system.
- `clientcode/database`: Scripts for database setup and management.
- `clientcode/device`: Scripts for obtaining device information.
- `clientcode/reports`: Scripts for generating reports from the collected data.
- `clientcode/setup`: Scripts for setting up the project, including API credential configuration and cron job setup.
- `clientcode/station`: Scripts for obtaining station information.
- `clientcode/strategy`: Scripts for implementing different energy management strategies.

## Building and Running

### 1. Initial Setup

The first step is to set up the API credentials. This is done by running the `setup_token.sh` script:

```bash
bash clientcode/setup/setup_token.sh
```

This script will prompt for your DeyeCloud email, password, AppId, and AppSecret. It will then obtain an access token and store all the necessary credentials in the `clientcode/variable.py` file.

### 2. Database Setup

Once the credentials are configured, you need to set up the SQLite database. This is done by running the `db_setup.py` script:

```bash
python3 clientcode/database/manage/db_setup.py
```

This script will create the `solar_data.db` file in the `clientcode/database` directory and set up the necessary tables.

### 3. Data Collection

The project is designed to automatically collect data every day using a cron job. To set up the cron job, run the `setup_cron.py` script:

```bash
python3 clientcode/setup/cron/setup_cron.py
```

This will set up a cron job that runs the `daily_update.py` script every day at 6 AM. This script fetches the previous day's data from the DeyeCloud API and stores it in the local database.

You can also manually backfill data for a specific period using the `backfill_data.py` and `backfill_daily_logs.py` scripts in the `clientcode/database/manage` directory.

### 4. Running Reports

Once you have collected some data, you can generate reports using the scripts in the `clientcode/reports` directory. For example, to view a summary of the frame-level data for a specific date, you can run:

```bash
python3 clientcode/reports/frame_summary.py --date 2025-01-15
```

## Development Conventions

- The project is written in Python 3.
- It uses the `requests` library for making API calls and the `sqlite3` library for database interaction.
- The project is intended to be run from the root directory.
- Scripts that interact with the DeyeCloud API rely on credentials stored in `clientcode/variable.py`.
- The database schema is defined in `clientcode/database/manage/db_setup.py`.
- The core data collection logic is in `clientcode/setup/cron/daily_update.py`.
- Control scripts in `clientcode/commission` allow for direct interaction with the solar energy system.
- The `clientcode/strategy` directory contains scripts for implementing different energy management strategies.
