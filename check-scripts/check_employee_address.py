"""
Check if Workwize API has address data for employee 952782
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
EMPLOYEE_ID = '952782'

headers = {
    'Authorization': f'Bearer {WORKWIZE_KEY}',
    'Accept': 'application/json'
}

# Try to get address data
url = f'https://prod-back.goworkwize.com/api/public/employees/{EMPLOYEE_ID}/addresses'
print(f"Checking: {url}\n")

try:
    response = requests.get(url, headers=headers, verify=False, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ SUCCESS! Address data found:")
        print(json.dumps(data, indent=2))
        
        # Extract country if available
        if isinstance(data, dict):
            if data.get('country'):
                print(f"\nCountry found: {data['country']}")
            if data.get('address'):
                addr = data['address']
                if isinstance(addr, dict) and addr.get('country'):
                    print(f"\nCountry in nested address: {addr['country']}")
    elif response.status_code == 404:
        print("✗ No address data found (404)")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"✗ Exception: {str(e)}")
