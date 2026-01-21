#!/usr/bin/env python3
"""
Setup cron job for daily solar data updates
Creates a cron job that runs daily_update.py every day at 6 AM
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_PATH = os.path.join(BASE_DIR, 'venv', 'bin', 'python')
SCRIPT_PATH = os.path.join(BASE_DIR, 'daily_update.py')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'cron.log')

def create_log_directory():
    """Create logs directory if it doesn't exist"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"✓ Created logs directory: {LOG_DIR}")

def get_current_crontab():
    """Get current crontab entries"""
    try:
        result = subprocess.run(['crontab', '-l'],
                              capture_output=True,
                              text=True,
                              check=False)
        if result.returncode == 0:
            return result.stdout
        return ""
    except Exception as e:
        print(f"Warning: Could not read current crontab: {e}")
        return ""

def setup_cron():
    """Setup cron job"""
    # Create logs directory
    create_log_directory()

    # Cron job line - runs daily at 6:00 AM
    cron_job = f"0 6 * * * cd {BASE_DIR} && {PYTHON_PATH} {SCRIPT_PATH} >> {LOG_PATH} 2>&1"

    # Get current crontab
    current_crontab = get_current_crontab()

    # Check if job already exists
    if 'daily_update.py' in current_crontab:
        print("⚠ Cron job already exists!")
        print("\nCurrent entry:")
        for line in current_crontab.split('\n'):
            if 'daily_update.py' in line:
                print(f"  {line}")

        response = input("\nDo you want to update it? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return

        # Remove old entry
        lines = [line for line in current_crontab.split('\n')
                if 'daily_update.py' not in line and line.strip()]
        current_crontab = '\n'.join(lines)
        if current_crontab:
            current_crontab += '\n'

    # Add new job
    new_crontab = current_crontab + cron_job + '\n'

    # Write to temp file
    temp_file = '/tmp/temp_crontab'
    with open(temp_file, 'w') as f:
        f.write(new_crontab)

    # Install new crontab
    try:
        subprocess.run(['crontab', temp_file], check=True)
        os.remove(temp_file)

        print("\n✓ Cron job installed successfully!")
        print("\nSchedule: Daily at 6:00 AM")
        print(f"Command: {cron_job}")
        print(f"Logs: {LOG_PATH}")

        print("\nTo view your crontab:")
        print("  crontab -l")

        print("\nTo remove the cron job:")
        print("  crontab -e")
        print("  (then delete the line containing 'daily_update.py')")

        print("\nTo view logs:")
        print(f"  tail -f {LOG_PATH}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing cron job: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

def test_script():
    """Test if daily_update.py can run"""
    print("Testing daily_update.py...")

    if not os.path.exists(PYTHON_PATH):
        print(f"✗ Python not found at: {PYTHON_PATH}")
        print("  Make sure you have created the virtual environment.")
        return False

    if not os.path.exists(SCRIPT_PATH):
        print(f"✗ Script not found at: {SCRIPT_PATH}")
        return False

    print("✓ All files found")

    response = input("\nDo you want to run a test now? (y/n): ")
    if response.lower() == 'y':
        print("\nRunning test...")
        result = subprocess.run([PYTHON_PATH, SCRIPT_PATH],
                              capture_output=True,
                              text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        if result.returncode == 0:
            print("✓ Test successful!")
            return True
        else:
            print("✗ Test failed. Please check the errors above.")
            return False

    return True

def main():
    """Main execution"""
    print("="*60)
    print("Solar Data Daily Update - Cron Setup")
    print("="*60)

    print(f"\nBase directory: {BASE_DIR}")
    print(f"Python: {PYTHON_PATH}")
    print(f"Script: {SCRIPT_PATH}")

    # Test script
    if not test_script():
        print("\n✗ Setup cancelled due to test failure")
        return 1

    # Setup cron
    print()
    if setup_cron():
        print("\n" + "="*60)
        print("Setup complete!")
        print("="*60)
        return 0
    else:
        print("\n✗ Setup failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
