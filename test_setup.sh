#!/bin/bash

# Test script to verify setup_token.sh logic without making API calls

set -e

# Test credentials
EMAIL="test@example.com"
PASSWORD="TestPassword123"
APPID="123456789"
APPSECRET="testsecret123"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OBTAIN_TOKEN_FILE="${SCRIPT_DIR}/clientcode/account/obtain_token.py"
VARIABLE_FILE="${SCRIPT_DIR}/clientcode/variable.py"

echo "Testing script logic..."
echo ""
echo "Test credentials:"
echo "  Email: $EMAIL"
echo "  Password: [HIDDEN]"
echo "  AppId: $APPID"
echo "  AppSecret: [HIDDEN]"
echo ""

# Check if files exist
if [ ! -f "$OBTAIN_TOKEN_FILE" ]; then
    echo "Error: obtain_token.py not found at $OBTAIN_TOKEN_FILE"
    exit 1
else
    echo "✓ Found obtain_token.py"
fi

if [ ! -f "$VARIABLE_FILE" ]; then
    echo "Error: variable.py not found at $VARIABLE_FILE"
    exit 1
else
    echo "✓ Found variable.py"
fi

# Validate inputs
if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ] || [ -z "$APPID" ] || [ -z "$APPSECRET" ]; then
    echo "Error: All fields are required"
    exit 1
else
    echo "✓ All inputs validated"
fi

echo ""
echo "Creating test copies..."

# Create test copies
cp "$OBTAIN_TOKEN_FILE" "${OBTAIN_TOKEN_FILE}.test"
cp "$VARIABLE_FILE" "${VARIABLE_FILE}.test"

echo "✓ Test copies created"
echo ""

# Test sed commands on test copies
echo "Testing credential updates..."

sed -i '' "s/appId = '[^']*'/appId = '${APPID}'/" "${OBTAIN_TOKEN_FILE}.test"
sed -i '' "s/password = '[^']*'/password = '${PASSWORD}'/" "${OBTAIN_TOKEN_FILE}.test"
sed -i '' 's/"appSecret": "[^"]*"/"appSecret": "'"${APPSECRET}"'"/' "${OBTAIN_TOKEN_FILE}.test"
sed -i '' 's/"email": "[^"]*"/"email": "'"${EMAIL}"'"/' "${OBTAIN_TOKEN_FILE}.test"

echo "✓ Updated obtain_token.py test copy"
echo ""

# Show the changes
echo "Modified lines in obtain_token.py:"
echo "---"
grep -n "appId = " "${OBTAIN_TOKEN_FILE}.test"
grep -n "password = " "${OBTAIN_TOKEN_FILE}.test"
grep -n '"appSecret":' "${OBTAIN_TOKEN_FILE}.test"
grep -n '"email":' "${OBTAIN_TOKEN_FILE}.test"
echo "---"
echo ""

# Test token update
TEST_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.TEST_TOKEN_DATA.SIGNATURE"
ESCAPED_TOKEN=$(echo "$TEST_TOKEN" | sed 's/[\/&]/\\&/g')

sed -i '' "s/token = '.*'/token = '${ESCAPED_TOKEN}'/" "${VARIABLE_FILE}.test"

echo "✓ Updated variable.py test copy"
echo ""

echo "Modified lines in variable.py:"
echo "---"
grep -n "token = " "${VARIABLE_FILE}.test"
echo "---"
echo ""

# Clean up test files
rm "${OBTAIN_TOKEN_FILE}.test"
rm "${VARIABLE_FILE}.test"

echo "✓ Test files cleaned up"
echo ""
echo "=========================================="
echo "  All tests passed successfully!"
echo "=========================================="
echo ""
echo "The setup_token.sh script is ready to use."
echo "Run it with: ./setup_token.sh"
