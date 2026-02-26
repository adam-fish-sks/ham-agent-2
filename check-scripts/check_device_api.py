"""
Check if Workwize API has device-specific endpoint with warehouse data
"""

import os
import requests
import json
import urllib3
from dotenv import load_dotenv

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')
DEVICE_SERIAL = 'CR8QCY3'
ASSET_ID = '118754495'  # From database

# Try different possible endpoints
endpoints = [
    f'https://prod-back.goworkwize.com/api/public/assets/{ASSET_ID}',
    f'https://prod-back.goworkwize.com/api/public/devices/{ASSET_ID}',
    f'https://prod-back.goworkwize.com/api/public/devices/{DEVICE_SERIAL}',
    f'https://prod-back.goworkwize.com/api/public/assets/{DEVICE_SERIAL}',
    'https://prod-back.goworkwize.com/api/public/devices?serial_number=' + DEVICE_SERIAL,
    'https://prod-back.goworkwize.com/api/public/assets?serial_code=' + DEVICE_SERIAL,
]

headers = {
    'Authorization': f'Bearer {WORKWIZE_KEY}',
    'Accept': 'application/json'
}

print(f"Checking Workwize API for device {DEVICE_SERIAL}...\n")

for endpoint in endpoints:
    print(f"Trying: {endpoint}")
    try:
        response = requests.get(endpoint, headers=headers, verify=False, timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ SUCCESS! Found data")
            print(f"\n  Full response:")
            print(json.dumps(data, indent=2))
            
            # Check for warehouse-related fields
            if isinstance(data, dict):
                warehouse_fields = [k for k in data.keys() if 'warehouse' in k.lower() or 'location' in k.lower()]
                if warehouse_fields:
                    print(f"\n  Warehouse/Location fields found: {warehouse_fields}")
                    for field in warehouse_fields:
                        print(f"    {field}: {data[field]}")
            break
        elif response.status_code == 404:
            print(f"  ✗ Not found (404)")
        else:
            print(f"  ✗ Error: {response.status_code}")
            print(f"    {response.text[:200]}")
    except Exception as e:
        print(f"  ✗ Exception: {str(e)[:100]}")
    print()
