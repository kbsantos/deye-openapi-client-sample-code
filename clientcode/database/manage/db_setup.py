#!/usr/bin/env python3
"""
Database setup script for solar system daily data
Creates SQLite database with tables for storing historical solar data
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'solar_data.db')

def create_database():
    """Create database and tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create daily_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE,
        station_id INTEGER NOT NULL,
        generation_kwh REAL,
        grid_feedin_kwh REAL,
        grid_purchase_kwh REAL,
        battery_charge_kwh REAL,
        battery_discharge_kwh REAL,
        consumption_kwh REAL,
        full_power_hours REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create index on date for faster queries
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_date ON daily_data(date)
    ''')

    # Create station_info table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS station_info (
        station_id INTEGER PRIMARY KEY,
        station_name TEXT,
        installed_capacity REAL,
        location_address TEXT,
        grid_type TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create daily_logs table for detailed solar metrics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        station_id INTEGER NOT NULL,
        production_kw REAL,
        consumption_kw REAL,
        grid_kw REAL,
        battery_kw REAL,
        soc_percent REAL,
        pv_kw REAL,
        generator_kw REAL,
        grid_tied_inverter_power_kw REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (station_id) REFERENCES station_info(station_id),
        UNIQUE(timestamp, station_id)
    )
    ''')

    # Create index on timestamp for faster queries
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_daily_logs_timestamp ON daily_logs(timestamp)
    ''')

    # Create index on station_id for faster queries
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_daily_logs_station_id ON daily_logs(station_id)
    ''')

    # Create unique index for preventing duplicates
    cursor.execute('''
    CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_logs_unique ON daily_logs(timestamp, station_id)
    ''')


    # Create index on date for faster queries
    cursor.execute('''
      DROP TABLE IF EXISTS grid_rates;
    ''')


    # Create grid_rate table
    cursor.execute('''
    CREATE TABLE grid_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
        sell_rate_kwh REAL,
        buy_rate_kwh REAL
    )
    ''')

    rates = [
        (1, 2024, 6,  9.76, 0),
        (2, 2024, 7, 11.91, 0),
        (3, 2024, 8, 11.91, 0),
        (4, 2024, 9, 11.91, 0),
        (5, 2024, 10, 11.91, 0),
        (6, 2024, 11, 11.91, 0),
        (7, 2024, 12, 11.91, 0),
        (8, 2025, 1, 11.53, 0),
        (9, 2025, 2,  7.25, 0),
        (10, 2025, 3,  2.47, 0),
        (11, 2025, 4, 11.29, 0),
        (12, 2025, 5, 10.92, 0),
        (13, 2025, 6, 11.29, 0),
        (14, 2025, 7, 11.29, 0),
        (15, 2025, 8, 10.54, 0),
        (16, 2025, 9, 10.48, 0),
        (17, 2025, 10, 10.54, 4.53),
        (18, 2025, 11, 10.54, 4.53),
        (19, 2025, 12, 10.54, 4.53)
    ]

    cursor.executemany(
        """
        INSERT INTO grid_rates
        (id, year, month, sell_rate_kwh, buy_rate_kwh)
        VALUES (?, ?, ?, ?, ?)
        """,
        rates
    )



    conn.commit()
    conn.close()

    print(f"Database created successfully at: {DB_PATH}")

if __name__ == '__main__':
    create_database()