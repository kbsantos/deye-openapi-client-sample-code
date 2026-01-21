# Project Overview

This project is a Python-based data collection and analysis tool for a solar energy system that uses the DeyeCloud API. It fetches daily and historical data from the API, stores it in a local SQLite database, and provides scripts to analyze and view the data.

## Key Technologies

*   **Language:** Python 3
*   **Libraries:** `requests`, `sqlite3`
*   **API:** DeyeCloud API v1
*   **Database:** SQLite

## Project Structure

The project is organized into a main directory containing scripts for data collection, database management, and analysis, and a `clientcode` directory that contains the code for interacting with the DeyeCloud API.

### Main Directory

*   `db_setup.py`: Initializes the SQLite database and creates the necessary tables.
*   `daily_update.py`: Fetches the previous day's data from the DeyeCloud API and saves it to the database. This script is intended to be run daily.
*   `backfill_data.py`: Fills the database with historical data for a specified date range.
*   `view_data.py`: A command-line tool to view the data stored in the database. It can display recent data, data for a specific date range, and monthly summaries.
*   `summary_data.py`: A command-line tool for more advanced data analysis, including monthly and yearly summaries, and a return on investment (ROI) calculation.
*   `install_cron.sh`: A shell script to install a cron job that runs `daily_update.py` automatically every day.
*   `setup_token.sh`: A shell script that likely automates the process of obtaining and configuring the API access token.
*   `README.md`: The main README file for the project.
*   `README_DATABASE.md`: A README file with details about the database schema.
*   `SETUP_README.md`: A README file with setup instructions.

### `clientcode` Directory

This directory contains the Python code for interacting with the DeyeCloud API.

*   `variable.py`: This file likely contains global variables such as the API base URL and headers.
*   `account/obtain_token.py`: A script to obtain an access token from the DeyeCloud API.
*   The `commission`, `device`, `station`, and `strategy` directories contain scripts for interacting with different endpoints of the DeyeCloud API.

## Building and Running

### 1. Prerequisites

*   Python 3
*   `requests` library (`pip install requests`)

### 2. Setup

1.  **Create a DeyeCloud account and application:** Follow the instructions in the [DeyeCloud API Documentation](https://developer.deyecloud.com/api) to create an account and an application to get your `appId` and `appSecret`.
2.  **Configure API credentials:** Edit `clientcode/account/obtain_token.py` and replace the placeholder values for `appId`, `appSecret`, `email`, and `password` with your actual credentials.
3.  **Obtain an access token:** Run the `clientcode/account/obtain_token.py` script to obtain an access token. This token will be used to authenticate with the API. The token should be placed in the `clientcode/variable.py` file.
4.  **Set up the database:** Run the `db_setup.py` script to create the `solar_data.db` SQLite database.

### 3. Running the Scripts

*   **Daily Updates:** The `daily_update.py` script is designed to be run automatically by a cron job. You can set up the cron job by running the `install_cron.sh` script.
*   **Viewing Data:** Use the `view_data.py` script to view the data in the database.
*   **Analyzing Data:** Use the `summary_data.py` script to perform more advanced analysis of the data.

## Development Conventions

*   The project uses the `requests` library for making HTTP requests to the DeyeCloud API.
*   Data is stored in a SQLite database.
*   The project is structured with a clear separation between the main application logic and the API client code.
*   Shell scripts are provided for automating setup and recurring tasks.
