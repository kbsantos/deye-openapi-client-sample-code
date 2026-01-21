#!/usr/bin/env python3
"""
Script to manage grid_rates in the solar_data.db database
"""

import sqlite3
import os
import argparse

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'solar_data.db')

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def add_rate(year, month, sell_rate, buy_rate):
    """Add a new grid rate"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO grid_rates (year, month, sell_rate_kwh, buy_rate_kwh)
            VALUES (?, ?, ?, ?)
            """,
            (year, month, sell_rate, buy_rate)
        )
        conn.commit()
        print(f"Successfully added rate for {year}-{month:02d}")
    except sqlite3.IntegrityError:
        print(f"Error: Rate for {year}-{month:02d} already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def update_rate(rate_id, year, month, sell_rate, buy_rate):
    """Update an existing grid rate"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE grid_rates
            SET year = ?, month = ?, sell_rate_kwh = ?, buy_rate_kwh = ?
            WHERE id = ?
            """,
            (year, month, sell_rate, buy_rate, rate_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Successfully updated rate with ID {rate_id}")
        else:
            print(f"Error: Rate with ID {rate_id} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def delete_rate(rate_id):
    """Delete a grid rate"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM grid_rates WHERE id = ?", (rate_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Successfully deleted rate with ID {rate_id}")
        else:
            print(f"Error: Rate with ID {rate_id} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def view_rates():
    """View all grid rates"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM grid_rates ORDER BY year, month")
        rates = cursor.fetchall()
        if rates:
            print(f"{'ID':<5} {'Year':<6} {'Month':<6} {'Sell Rate':<12} {'Buy Rate':<12}")
            print("-" * 45)
            for rate in rates:
                print(f"{rate['id']:<5} {rate['year']:<6} {rate['month']:<6} {rate['sell_rate_kwh']:<12.2f} {rate['buy_rate_kwh']:<12.2f}")
        else:
            print("No grid rates found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Manage grid rates in the solar database.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new rate')
    parser_add.add_argument('year', type=int, help='Year (e.g., 2026)')
    parser_add.add_argument('month', type=int, help='Month (1-12)')
    parser_add.add_argument('sell_rate', type=float, help='Sell rate per kWh')
    parser_add.add_argument('buy_rate', type=float, help='Buy rate per kWh')

    # Update command
    parser_update = subparsers.add_parser('update', help='Update an existing rate')
    parser_update.add_argument('id', type=int, help='ID of the rate to update')
    parser_update.add_argument('year', type=int, help='Year (e.g., 2026)')
    parser_update.add_argument('month', type=int, help='Month (1-12)')
    parser_update.add_argument('sell_rate', type=float, help='Sell rate per kWh')
    parser_update.add_argument('buy_rate', type=float, help='Buy rate per kWh')

    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete a rate')
    parser_delete.add_argument('id', type=int, help='ID of the rate to delete')

    # View command
    parser_view = subparsers.add_parser('view', help='View all rates')

    args = parser.parse_args()

    if args.command == 'add':
        add_rate(args.year, args.month, args.sell_rate, args.buy_rate)
    elif args.command == 'update':
        update_rate(args.id, args.year, args.month, args.sell_rate, args.buy_rate)
    elif args.command == 'delete':
        delete_rate(args.id)
    elif args.command == 'view':
        view_rates()
    else:
        parser.print_help()
