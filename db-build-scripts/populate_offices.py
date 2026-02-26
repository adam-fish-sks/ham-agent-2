"""
Populate Offices Table from Workwize API

This script fetches office data from the Workwize API and populates the PostgreSQL
offices table. No PII scrubbing needed as offices are business locations.

Note: The /offices endpoint may return 404 if not available for the account tier.

Usage:
    python populate_offices.py
"""

import os
import sys
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from dotenv import load_dotenv
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Configuration
WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
WORKWIZE_BASE_URL = 'https://prod-back.goworkwize.com/api/public'


def fetch_offices():
    """Fetch all offices from Workwize API with pagination."""
    all_offices = []
    page = 1
    
    headers = {
        'Authorization': f'Bearer {WORKWIZE_KEY}',
        'Accept': 'application/json'
    }
    
    while True:
        url = f'{WORKWIZE_BASE_URL}/offices?page={page}'
        print(f"Fetching page {page} from {url}...")
        
        try:
            response = requests.get(url, headers=headers, verify=False)
            
            # Check if endpoint exists
            if response.status_code == 404:
                print("⚠️  The /offices endpoint returned 404 Not Found")
                print("   This endpoint may not be available for this account tier")
                return []
            
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, dict):
                if 'data' in data:
                    offices = data['data']
                elif 'value' in data:
                    offices = data['value']
                else:
                    offices = [data]
                
                # Add to collection
                all_offices.extend(offices)
                
                # Check pagination info
                meta = data.get('meta', {})
                links = data.get('links', {})
                
                current_page = meta.get('current_page', page)
                last_page = meta.get('last_page')
                total = meta.get('total', 0)
                
                print(f"  Page {current_page}: Fetched {len(offices)} offices (Total so far: {len(all_offices)}/{total})")
                
                # Check if there's a next page
                if not links.get('next') or (last_page and current_page >= last_page):
                    break
                
                page += 1
            else:
                # If it's just an array, no pagination
                all_offices = data
                break
        
        except requests.RequestException as e:
            print(f"❌ Error fetching offices: {e}")
            return []
    
    print(f"\n✅ Fetched {len(all_offices)} total offices")
    return all_offices


def transform_office(office):
    """Transform API office data to database format."""
    # Extract basic data
    office_id = str(office.get('id', ''))
    
    # Office name
    name = office.get('name') or f"Office {office_id}"
    
    # Office code
    code = office.get('code') or office.get('office_code')
    
    # Address ID - may need to look up from addresses table
    address_id = None
    if office.get('address'):
        if isinstance(office['address'], dict):
            addr_id = office['address'].get('id')
            if addr_id:
                address_id = str(addr_id)
        else:
            address_id = str(office['address'])
    elif office.get('address_id'):
        address_id = str(office['address_id'])
    
    # Contact info
    phone = office.get('phone') or office.get('phone_number')
    email = office.get('email') or office.get('contact_email')
    
    # Capacity
    capacity = office.get('capacity') or office.get('max_capacity')
    if capacity:
        try:
            capacity = int(capacity)
        except:
            capacity = None
    
    # Status
    status = office.get('status') or 'active'
    
    # Timestamps
    created_at = datetime.now()
    if office.get('created_at') or office.get('createdAt'):
        date_str = office.get('created_at') or office.get('createdAt')
        try:
            created_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    updated_at = datetime.now()
    if office.get('updated_at') or office.get('updatedAt'):
        date_str = office.get('updated_at') or office.get('updatedAt')
        try:
            updated_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    return (
        office_id,
        name,
        code,
        address_id,
        phone,
        email,
        capacity,
        status,
        created_at,
        updated_at
    )


def populate_offices(offices):
    """Insert offices into PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Transform all offices
        office_data = [transform_office(office) for office in offices]
        
        # Insert query with ON CONFLICT to handle duplicates
        insert_query = """
            INSERT INTO offices (
                id, name, code, "addressId", phone, email,
                capacity, status, "createdAt", "updatedAt"
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                code = EXCLUDED.code,
                "addressId" = EXCLUDED."addressId",
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                capacity = EXCLUDED.capacity,
                status = EXCLUDED.status,
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        # Execute batch insert
        execute_values(cursor, insert_query, office_data)
        
        conn.commit()
        print(f"✅ Successfully inserted/updated {len(office_data)} offices")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM offices")
        total = cursor.fetchone()[0]
        print(f"📊 Total offices in database: {total}")
        
        cursor.execute("SELECT status, COUNT(*) FROM offices GROUP BY status ORDER BY COUNT(*) DESC")
        status_counts = cursor.fetchall()
        if status_counts:
            print("\n📈 Offices by status:")
            for status, count in status_counts:
                print(f"  {status or 'Unknown'}: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM offices WHERE \"addressId\" IS NOT NULL")
        with_address = cursor.fetchone()[0]
        print(f"\n🏢 Offices with addresses: {with_address}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting offices: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function."""
    print("=" * 60)
    print("Workwize Office Population Script")
    print("=" * 60)
    
    # Validate environment variables
    if not WORKWIZE_KEY:
        print("❌ Error: WORKWIZE_KEY not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Fetch offices from API
        offices = fetch_offices()
        
        if not offices:
            print("⚠️  No offices found in API response")
            print("   The offices table will remain empty")
            print("   This is expected if the endpoint is not available for this account")
            return
        
        # Populate database
        populate_offices(offices)
        
        print("\n✅ Office population complete!")
        
    except requests.RequestException as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"❌ Database Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
