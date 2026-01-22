# Deye Solar API Postman Collection
 
This Postman collection contains all the API endpoints from your Python scripts for the Deye Solar Cloud Platform.
 
## Setup Instructions
 
### 1. Import Collection
1. Open Postman
2. Click "Import" in the top left
3. Select "Upload Files"
4. Choose `postman_collection.json` from this project
 
### 2. Configure Environment Variables
Before using the collection, set these variables in Postman:
 
#### Required Variables:
- `base_url`: `https://eu.deyecloud.com` (pre-filled)
- `app_id`: Your application ID from Deye Cloud
- `password_sha256`: SHA256 hash of your password
- `access_token`: Will be automatically set after authentication
 
#### Optional Variables:
- `station_id`: Your station ID (get from station list)
- `device_id`: Your device ID (get from device list)
- `start_time`: Start time for history queries (ISO format)
- `end_time`: End time for history queries (ISO format)
 
### 3. Generate Password Hash
Use this Python script to generate your SHA256 password hash:
 
```python
import hashlib
 
password = 'your_password_here'
sha256_hash = hashlib.sha256()
sha256_hash.update(password.encode('utf-8'))
password_with_256 = sha256_hash.hexdigest()
print(password_with_256)
```
 
## API Endpoints Included
 
### Authentication
- **Obtain Token**: Get access token using credentials
- **Account Info**: Get account information
 
### Station Management
- **Get Station List**: List all stations
- **Get Station Latest Data**: Get latest station data
- **Get Station History**: Get historical station data
 
### Device Management
- **Get Device List**: List all devices
- **Get Device Latest Data**: Get latest device data
- **Get Device History**: Get historical device data
 
### Reports
- **Get Summary Data**: Get summary reports
 
## Usage Flow
 
1. **Set environment variables** (app_id, password_sha256)
2. **Run "Obtain Token"** to get access token
3. **Copy the token** from response to `access_token` variable
4. **Run "Get Station List"** to get your station_id
5. **Use other endpoints** with proper IDs
 
## Notes
 
- All requests use POST method as per the original API
- Authorization header uses Bearer token format
- Time parameters should be in ISO format
- The collection follows the same structure as your Python scripts