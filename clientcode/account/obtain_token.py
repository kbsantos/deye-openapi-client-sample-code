#!/usr/bin/env python3
"""
Obtain authentication token from Deye Solar API
Uses configuration variables from variable.py
"""

import hashlib
import json
import requests
import sys
import os

# Add project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from clientcode import variable

if __name__ == '__main__':
    url = variable.baseurl + '/account/token?appId=' + variable.app_id
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Hash the password
    sha256_hash = hashlib.sha256()
    sha256_hash.update(variable.password.encode('utf-8'))
    password_with_256 = sha256_hash.hexdigest()
    
    data = {
        "appSecret": variable.app_secret,
        "email": variable.email,
        "companyId": variable.company_id,
        "password": password_with_256
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        print(json.dumps(response.json(), indent=2))

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Error occurred: {err}")
