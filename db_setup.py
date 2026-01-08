#!/usr/bin/env python3
"""
Database setup script for solar system daily data
Creates SQLite database with tables for storing historical solar data
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'solar_data.db')

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

    conn.commit()
    conn.close()

    print(f"Database created successfully at: {DB_PATH}")

if __name__ == '__main__':
    create_database()
