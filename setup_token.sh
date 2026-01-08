#!/bin/bash

# Script to obtain and configure Deye API token
# This script will prompt for credentials, update obtain_token.py, get the token, and update variable.py

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OBTAIN_TOKEN_FILE="${SCRIPT_DIR}/clientcode/account/obtain_token.py"
VARIABLE_FILE="${SCRIPT_DIR}/clientcode/variable.py"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Deye API Token Setup${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if files exist
if [ ! -f "$OBTAIN_TOKEN_FILE" ]; then
    echo -e "${RED}Error: obtain_token.py not found at $OBTAIN_TOKEN_FILE${NC}"
    exit 1
fi

if [ ! -f "$VARIABLE_FILE" ]; then
    echo -e "${RED}Error: variable.py not found at $VARIABLE_FILE${NC}"
    exit 1
fi

# Prompt for credentials
read -p "Enter Email: " EMAIL
read -s -p "Enter Password: " PASSWORD
echo ""
read -p "Enter AppId: " APPID
read -s -p "Enter AppSecret: " APPSECRET
echo ""
echo ""

# Validate inputs
if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ] || [ -z "$APPID" ] || [ -z "$APPSECRET" ]; then
    echo -e "${RED}Error: All fields are required${NC}"
    exit 1
fi

echo -e "${BLUE}Updating obtain_token.py with credentials...${NC}"

# Create backup
cp "$OBTAIN_TOKEN_FILE" "${OBTAIN_TOKEN_FILE}.bak"
echo -e "${GREEN}Backup created: ${OBTAIN_TOKEN_FILE}.bak${NC}"

# Update obtain_token.py with sed (macOS compatible)
sed -i '' "s/appId = '[^']*'/appId = '${APPID}'/" "$OBTAIN_TOKEN_FILE"
sed -i '' "s/password = '[^']*'/password = '${PASSWORD}'/" "$OBTAIN_TOKEN_FILE"
sed -i '' 's/"appSecret": "[^"]*"/"appSecret": "'"${APPSECRET}"'"/' "$OBTAIN_TOKEN_FILE"
sed -i '' 's/"email": "[^"]*"/"email": "'"${EMAIL}"'"/' "$OBTAIN_TOKEN_FILE"

echo -e "${GREEN}Credentials updated successfully${NC}"
echo ""

# Run obtain_token.py and capture output
echo -e "${BLUE}Obtaining token from Deye API...${NC}"
cd "$SCRIPT_DIR/clientcode/account"

# Check if venv exists and activate it
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    echo -e "${GREEN}Virtual environment activated${NC}"
fi

# Run the script and capture output
OUTPUT=$(python3 obtain_token.py 2>&1)
echo "$OUTPUT"

# Extract token from JSON response using Python
TOKEN=$(echo "$OUTPUT" | python3 -c "
import sys
import json
import re

# Read all input
input_text = sys.stdin.read()

# Try to find JSON in the output
json_match = re.search(r'\{.*\}', input_text, re.DOTALL)
if json_match:
    try:
        data = json.loads(json_match.group())
        if 'data' in data and 'token' in data['data']:
            print(data['data']['token'])
        else:
            print('')
    except:
        print('')
else:
    print('')
" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Error: Failed to extract token from response${NC}"
    echo -e "${RED}Please check the output above for errors${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Token obtained successfully!${NC}"
echo -e "${BLUE}Token: ${TOKEN:0:50}...${NC}"
echo ""

# Update variable.py with the new token
echo -e "${BLUE}Updating variable.py with new token...${NC}"

# Create backup
cp "$VARIABLE_FILE" "${VARIABLE_FILE}.bak"
echo -e "${GREEN}Backup created: ${VARIABLE_FILE}.bak${NC}"

# Escape special characters in token for sed
ESCAPED_TOKEN=$(echo "$TOKEN" | sed 's/[\/&]/\\&/g')

# Update token in variable.py
sed -i '' "s/token = '.*'/token = '${ESCAPED_TOKEN}'/" "$VARIABLE_FILE"

echo -e "${GREEN}Token updated successfully in variable.py${NC}"
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Your token has been configured and is ready to use."
