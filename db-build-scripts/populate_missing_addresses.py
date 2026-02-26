#!/usr/bin/env python3

import os
import psycopg2
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dotenv import load_dotenv

# Suppress only the InsecureRequestWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable not set")

WORKWIZE_API_KEY = os.getenv('WORKWIZE_KEY')
if not WORKWIZE_API_KEY:
    raise Exception("WORKWIZE_KEY environment variable not set")

WORKWIZE_BASE_URL = 'https://prod-back.goworkwize.com/api/public/employees'

def fetch_employee_address(employee_id):
    """Fetch address for a specific employee from Workwize API"""
    url = f'{WORKWIZE_BASE_URL}/{employee_id}/addresses'
    headers = {
        'Authorization': f'Bearer {WORKWIZE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        time.sleep(0.01)  # 10ms rate limiting
        
        # Debug first 3 employees
        if employee_id in ['117576', '952782', '118662']:
            print(f"\nDEBUG employee {employee_id}:")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Success: {data.get('success')}")
                print(f"  Has data: {bool(data.get('data'))}")
                if data.get('data'):
                    print(f"  Data keys: {list(data['data'].keys())}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                address_data = data['data']
                
                # Extract country name - can be nested or direct
                country_name = None
                country_data = address_data.get('country')
                if isinstance(country_data, dict):
                    country_name = country_data.get('name')
                elif isinstance(country_data, str):
                    country_name = country_data
                
                if country_name:
                    return {
                        'id': str(address_data.get('id')),
                        'city': address_data.get('city'),
                        'region': address_data.get('region'),
                        'postalCode': address_data.get('postal_code') or address_data.get('postcode'),
                        'country': country_name
                    }
    except Exception as e:
        print(f"Error fetching address for employee {employee_id}: {e}")
    
    return None

def get_employees_without_addresses():
    """Get all employees that don't have an addressId"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute('SELECT id FROM employees WHERE "addressId" IS NULL ORDER BY id')
    employee_ids = [row[0] for row in cur.fetchall()]
    
    conn.close()
    return employee_ids

def populate_missing_addresses():
    """Populate addresses for employees that don't have them"""
    print("Finding employees without addresses...")
    employee_ids = get_employees_without_addresses()
    
    if not employee_ids:
        print("All employees have addresses!")
        return
    
    print(f"Found {len(employee_ids)} employees without addresses")
    print("Fetching addresses from Workwize API...")
    
    # Fetch addresses with parallel processing
    addresses_to_create = {}
    employee_address_map = {}
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_emp = {executor.submit(fetch_employee_address, emp_id): emp_id for emp_id in employee_ids}
        
        completed = 0
        for future in as_completed(future_to_emp):
            emp_id = future_to_emp[future]
            completed += 1
            
            if completed % 10 == 0:
                print(f"  Processed {completed}/{len(employee_ids)} employees")
            
            address = future.result()
            if address:
                address_id = address['id']
                addresses_to_create[address_id] = address
                employee_address_map[emp_id] = address_id
    
    print(f"\nFound addresses for {len(employee_address_map)} employees")
    
    if not employee_address_map:
        print("No addresses found to populate")
        return
    
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check which addresses already exist
    print("Checking for existing addresses...")
    address_ids = list(addresses_to_create.keys())
    cur.execute('SELECT id FROM addresses WHERE id = ANY(%s)', (address_ids,))
    existing_address_ids = set(row[0] for row in cur.fetchall())
    
    # Create new addresses
    new_addresses = [addr for addr_id, addr in addresses_to_create.items() if addr_id not in existing_address_ids]
    
    if new_addresses:
        print(f"Creating {len(new_addresses)} new addresses...")
        
        insert_query = """
            INSERT INTO addresses (id, city, region, "postalCode", country, "createdAt", "updatedAt")
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """
        
        for addr in new_addresses:
            cur.execute(insert_query, (
                addr['id'],
                addr['city'],
                addr['region'],
                addr['postalCode'],
                addr['country']
            ))
        
        conn.commit()
        print(f"✓ Created {len(new_addresses)} addresses")
    else:
        print("All addresses already exist in database")
    
    # Update employees with addressId
    print(f"Updating {len(employee_address_map)} employees with address links...")
    
    update_query = 'UPDATE employees SET "addressId" = %s WHERE id = %s'
    
    for emp_id, address_id in employee_address_map.items():
        cur.execute(update_query, (address_id, emp_id))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Updated {len(employee_address_map)} employees")
    print("\nDone! Address population complete.")
    
    # Show summary
    print(f"\nSummary:")
    print(f"  Employees processed: {len(employee_ids)}")
    print(f"  Addresses found: {len(employee_address_map)}")
    print(f"  Addresses not found: {len(employee_ids) - len(employee_address_map)}")
    print(f"  New addresses created: {len(new_addresses)}")

if __name__ == '__main__':
    populate_missing_addresses()
