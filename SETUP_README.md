# Deye API Token Setup Script

## Overview
The `setup_token.sh` script automates the process of obtaining and configuring your Deye API authentication token.

## Test Results

### ✓ Syntax Check
- No bash syntax errors detected
- Script structure is valid

### ✓ File Detection
- Successfully locates `obtain_token.py`
- Successfully locates `variable.py`
- Proper error handling if files are missing

### ✓ Credential Updates
- AppId: Updated correctly on line 13
- Password: Updated correctly on line 18
- AppSecret: Updated correctly on line 23
- Email: Updated correctly on line 24

### ✓ Token Extraction
- Successfully parses JSON response from API
- Correctly extracts token from `data.token` field
- Handles error responses gracefully

### ✓ Token Update
- Successfully updates `variable.py` with new token
- Properly escapes special characters in token

### ✓ Backup System
- Creates `.bak` files before modifications
- Allows for easy rollback if needed

## Usage

### Basic Usage
```bash
cd /Users/kris/Documents/Project/Deye/openApi
./setup_token.sh
```

### What the Script Does
1. Prompts for your credentials:
   - Email address
   - Password (hidden input)
   - AppId
   - AppSecret (hidden input)

2. Creates backups:
   - `obtain_token.py.bak`
   - `variable.py.bak`

3. Updates `obtain_token.py` with your credentials

4. Runs the script to obtain token from Deye API

5. Extracts the token from JSON response

6. Updates `variable.py` with the new token

### Output
The script provides color-coded output:
- 🔵 Blue: Information messages
- 🟢 Green: Success messages
- 🔴 Red: Error messages

### Example Session
```
======================================
  Deye API Token Setup
======================================

Enter Email: your-email@example.com
Enter Password:
Enter AppId: 202409175537006
Enter AppSecret:
```

## File Modifications

### obtain_token.py
Updates these lines:
- Line 13: `appId = 'YOUR_APPID'`
- Line 18: `password = 'YOUR_PASSWORD'`
- Line 23: `"appSecret": "YOUR_APPSECRET"`
- Line 24: `"email": "YOUR_EMAIL"`

### variable.py
Updates this line:
- Line 6: `token = 'YOUR_NEW_TOKEN'`

## Error Handling

The script includes error handling for:
- Missing input fields
- File not found errors
- Failed API requests
- Invalid JSON responses
- Token extraction failures

## Rollback

If you need to restore previous values:
```bash
# Restore obtain_token.py
cp clientcode/account/obtain_token.py.bak clientcode/account/obtain_token.py

# Restore variable.py
cp clientcode/variable.py.bak clientcode/variable.py
```

## Requirements

- bash shell
- python3 with requests library
- Active internet connection
- Valid Deye Cloud credentials

## Security Notes

- Passwords are hidden during input
- Backup files contain sensitive information
- Consider adding `*.bak` to `.gitignore`
- Do not commit credentials to version control

## Troubleshooting

### Script not executable
```bash
chmod +x setup_token.sh
```

### Python requests not found
```bash
source venv/bin/activate
pip install requests
```

### API returns error
- Verify your credentials are correct
- Check if your AppId and AppSecret are valid
- Ensure you're using the correct data center (EU/US)

## Testing

A test script is available to verify functionality:
```bash
./test_setup.sh
```

This performs a dry-run without making actual API calls.
