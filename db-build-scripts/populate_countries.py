"""
Populate Countries Table from Workwize API

This script fetches unique country data from employee addresses in the Workwize API
and populates the PostgreSQL countries table with no duplicates.

Usage:
    python populate_countries.py
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


def extract_country_data(address_data):
    """Extract country data from address object."""
    if not address_data:
        return None
    
    country_obj = address_data.get('country')
    if not country_obj or not isinstance(country_obj, dict):
        return None
    
    country_id = country_obj.get('id')
    if not country_id:
        return None
    
    # Convert to string ID
    country_id = str(country_id)
    
    # Extract all country fields
    name = country_obj.get('name')
    code = country_obj.get('code')
    requires_tin = bool(country_obj.get('requires_tin', False))
    invoice_currency = country_obj.get('invoice_currency')
    
    # Note: is_offboardable not in sample, but we'll check for it
    is_offboardable = bool(country_obj.get('is_offboardable', 1))
    
    if not name or not code:
        return None
    
    return {
        'id': country_id,
        'name': name,
        'code': code,
        'requires_tin': requires_tin,
        'invoice_currency': invoice_currency,
        'is_offboardable': is_offboardable
    }


def collect_unique_countries(employee_ids):
    """Fetch addresses for all employees and extract unique countries."""
    countries_dict = {}  # Using dict to ensure uniqueness by ID
    total_employees = len(employee_ids)
    
    print(f"Fetching addresses to extract country data from {total_employees} employees...\n")
    
    for idx, employee_id in enumerate(employee_ids, 1):
        # Progress indicator every 100 employees
        if idx % 100 == 0 or idx == 1:
            print(f"Progress: {idx}/{total_employees} ({idx*100//total_employees}%) - Found {len(countries_dict)} unique countries")
        
        # Fetch address
        address_data = fetch_employee_address(employee_id)
        
        if address_data:
            country_data = extract_country_data(address_data)
            if country_data:
                country_id = country_data['id']
                # Only add if not already seen
                if country_id not in countries_dict:
                    countries_dict[country_id] = country_data
        
        # Rate limiting
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    print(f"\n✅ Found {len(countries_dict)} unique countries\n")
    
    return list(countries_dict.values())


def populate_countries(countries):
    """Insert unique countries into database."""
    if not countries:
        print("No countries to insert")
        return
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        now = datetime.now()
        
        # Prepare data for insertion
        countries_to_insert = [
            (
                c['id'],
                c['name'],
                c['code'],
                c['requires_tin'],
                c['invoice_currency'],
                c['is_offboardable'],
                now,
                now
            )
            for c in countries
        ]
        
        # Insert countries
        insert_query = """
            INSERT INTO countries (
                id, name, code, "requiresTin", "invoiceCurrency", 
                "isOffboardable", "createdAt", "updatedAt"
            ) VALUES %s
            ON CONFLICT (code) DO UPDATE SET
                name = EXCLUDED.name,
                "requiresTin" = EXCLUDED."requiresTin",
                "invoiceCurrency" = EXCLUDED."invoiceCurrency",
                "isOffboardable" = EXCLUDED."isOffboardable",
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        execute_values(cursor, insert_query, countries_to_insert)
        conn.commit()
        
        print(f"✅ Successfully inserted/updated {len(countries_to_insert)} countries")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM countries")
        total = cursor.fetchone()[0]
        print(f"📊 Total countries in database: {total}\n")
        
        cursor.execute('SELECT name, code, "invoiceCurrency" FROM countries ORDER BY name')
        all_countries = cursor.fetchall()
        print("📋 Countries in database:")
        for name, code, currency in all_countries:
            currency_str = f" ({currency})" if currency else ""
            print(f"  {code}: {name}{currency_str}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting countries: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function."""
    print("=" * 60)
    print("Workwize Countries Population Script")
    print("=" * 60)
    
    # Validate environment variables
    if not WORKWIZE_KEY:
        print("❌ Error: WORKWIZE_KEY not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Get employee IDs
        print("\n📋 Fetching employee IDs from database...")
        employee_ids = get_employee_ids()
        print(f"✅ Found {len(employee_ids)} employees\n")
        
        # Collect unique countries from addresses
        countries = collect_unique_countries(employee_ids)
        
        # Populate countries table
        populate_countries(countries)
        
        print("\n" + "=" * 60)
        print("✅ Countries population completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
