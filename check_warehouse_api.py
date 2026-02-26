#!/usr/bin/env python3
"""Check what warehouse data the API returns"""
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
import json

project_root = Path(__file__).parent
load_dotenv(project_root / '.env')

WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')
BASE_URL = "https://prod-back.goworkwize.com/api/public"

headers = {
    'Authorization': f'Bearer {WORKWIZE_KEY}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

# Fetch first warehouse
response = requests.get(f'{BASE_URL}/warehouses?page=1', headers=headers, verify=False)
data = response.json()

if isinstance(data, dict) and 'data' in data:
    warehouses = data['data']
else:
    warehouses = data

if warehouses:
    print("Sample warehouse data from API:")
    print(json.dumps(warehouses[0], indent=2))
else:
    print("No warehouses returned")
