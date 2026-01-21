#!/bin/bash
# Install cron job for daily solar data updates

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python"
UPDATE_SCRIPT="$SCRIPT_DIR/daily_update.py"
LOG_FILE="$SCRIPT_DIR/logs/cron.log"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Cron job line
CRON_JOB="0 6 * * * cd $SCRIPT_DIR && $PYTHON_PATH $UPDATE_SCRIPT >> $LOG_FILE 2>&1"

# Check if job already exists
crontab -l 2>/dev/null | grep -q "daily_update.py"
if [ $? -eq 0 ]; then
    echo "⚠ Cron job already exists!"
    echo "Current cron job:"
    crontab -l | grep daily_update.py
    echo ""
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    # Remove old job
    crontab -l | grep -v "daily_update.py" | crontab -
fi

# Add new job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "✓ Cron job installed successfully!"
echo ""
echo "Schedule: Daily at 6:00 AM"
echo "Command: $CRON_JOB"
echo ""
echo "Logs will be saved to: $LOG_FILE"
echo ""
echo "To view your crontab:"
echo "  crontab -l"
echo ""
echo "To view logs:"
echo "  tail -f $LOG_FILE"
echo ""
echo "To remove the cron job:"
echo "  crontab -e"
echo "  (then delete the line containing 'daily_update.py')"
echo ""
