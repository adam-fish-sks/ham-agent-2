"""
Populate Addresses Table from Workwize API

This script fetches address data for each employee from the Workwize API and populates 
the PostgreSQL addresses table with PII scrubbing applied (no street addresses stored).

Usage:
    python populate_addresses.py
"""

import os
import sys
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from dotenv import load_dotenv
import time
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Configuration
WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
WORKWIZE_BASE_URL = 'https://prod-back.goworkwize.com/api/public'

# Rate limiting
DELAY_BETWEEN_REQUESTS = 0.1  # 100ms delay to avoid overwhelming API


def get_employee_ids():
    """Get all employee IDs from the database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id FROM employees ORDER BY id')
        employee_ids = [row[0] for row in cursor.fetchall()]
        return employee_ids
    finally:
        cursor.close()
        conn.close()


def fetch_employee_address(employee_id):
    """Fetch address for a specific employee."""
    url = f'{WORKWIZE_BASE_URL}/employees/{employee_id}/addresses'
    headers = {
        'Authorization': f'Bearer {WORKWIZE_KEY}',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        # If 404, employee has no address
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        data = response.json()
        
        # Handle response format
        if isinstance(data, dict) and data.get('data'):
            return data['data']
        elif isinstance(data, dict) and data.get('success'):
            return data.get('data')
        
        return None
    except requests.exceptions.Timeout:
        print(f"  ⚠️  Timeout for employee {employee_id}")
        return None
    except requests.exceptions.RequestException as e:
        if hasattr(e.response, 'status_code') and e.response.status_code == 404:
            return None
        print(f"  ⚠️  Error fetching address for employee {employee_id}: {e}")
        return None


def transform_address(address_data, employee_id):
    """Transform API address data to database format with PII scrubbing."""
    if not address_data:
        return None
    
    # Extract address ID
    address_id = str(address_data.get('id', ''))
    if not address_id:
        return None
    
    # City - KEPT
    city = address_data.get('city')
    
    # Region/State - KEPT
    region = address_data.get('region') or address_data.get('state')
    
    # Country - KEPT (extract name from dict if needed)
    country = None
    country_data = address_data.get('country')
    if country_data:
        if isinstance(country_data, dict):
            country = country_data.get('name')
        else:
            country = str(country_data)
    
    # Postal code - KEPT (general location data)
    postal_code = address_data.get('postal_code') or address_data.get('postcode')
    
    # Latitude/Longitude - if available
    latitude = None
    longitude = None
    if address_data.get('latitude'):
        try:
            latitude = float(address_data['latitude'])
        except:
            pass
    if address_data.get('longitude'):
        try:
            longitude = float(address_data['longitude'])
        except:
            pass
    
    # Timestamps
    created_at = datetime.now()
    if address_data.get('created_at') or address_data.get('createdAt'):
        date_str = address_data.get('created_at') or address_data.get('createdAt')
        try:
            created_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    updated_at = datetime.now()
    if address_data.get('updated_at') or address_data.get('updatedAt'):
        date_str = address_data.get('updated_at') or address_data.get('updatedAt')
        try:
            updated_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    # NOTE: address_line_1, address_line_2 are INTENTIONALLY NOT STORED (PII scrubbing)
    
    return (
        address_id,
        city,
        region,
        country,
        postal_code,
        latitude,
        longitude,
        created_at,
        updated_at
    )


def populate_addresses(employee_ids):
    """Fetch addresses for all employees and insert into database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    addresses_to_insert = []
    total_employees = len(employee_ids)
    fetched_count = 0
    no_address_count = 0
    error_count = 0
    
    print(f"Fetching addresses for {total_employees} employees...\n")
    
    try:
        for idx, employee_id in enumerate(employee_ids, 1):
            # Progress indicator every 50 employees
            if idx % 50 == 0 or idx == 1:
                print(f"Progress: {idx}/{total_employees} ({idx*100//total_employees}%)")
            
            # Fetch address
            address_data = fetch_employee_address(employee_id)
            
            if address_data:
                transformed = transform_address(address_data, employee_id)
                if transformed:
                    addresses_to_insert.append(transformed)
                    fetched_count += 1
            else:
                no_address_count += 1
            
            # Rate limiting
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print(f"\n✅ Fetched {fetched_count} addresses")
        print(f"⚠️  {no_address_count} employees have no address")
        
        if not addresses_to_insert:
            print("No addresses to insert")
            return
        
        # Insert addresses
        insert_query = """
            INSERT INTO addresses (
                id, city, region, country, "postalCode",
                latitude, longitude, "createdAt", "updatedAt"
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                city = EXCLUDED.city,
                region = EXCLUDED.region,
                country = EXCLUDED.country,
                "postalCode" = EXCLUDED."postalCode",
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        execute_values(cursor, insert_query, addresses_to_insert)
        conn.commit()
        
        print(f"✅ Successfully inserted/updated {len(addresses_to_insert)} addresses")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM addresses")
        total = cursor.fetchone()[0]
        print(f"📊 Total addresses in database: {total}")
        
        cursor.execute("SELECT country, COUNT(*) FROM addresses WHERE country IS NOT NULL GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10")
        country_counts = cursor.fetchall()
        print("\n📈 Top 10 countries:")
        for country, count in country_counts:
            print(f"  {country}: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting addresses: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function."""
    print("=" * 60)
    print("Workwize Address Population Script")
    print("=" * 60)
    
    # Validate environment variables
    if not WORKWIZE_KEY:
        print("❌ Error: WORKWIZE_KEY not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Get employee IDs from database
        print("Fetching employee IDs from database...")
        employee_ids = get_employee_ids()
        print(f"Found {len(employee_ids)} employees\n")
        
        if not employee_ids:
            print("⚠️  No employees found in database")
            return
        
        # Fetch and populate addresses
        populate_addresses(employee_ids)
        
        print("\n✅ Address population complete!")
        print("\n⚠️  REMINDER: PII scrubbing applied:")
        print("  - address_line_1: NOT STORED (removed)")
        print("  - address_line_2: NOT STORED (removed)")
        print("  - Only city, region, country, postal_code stored")
        
    except psycopg2.Error as e:
        print(f"❌ Database Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
