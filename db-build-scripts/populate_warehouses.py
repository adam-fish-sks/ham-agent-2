"""
Populate Warehouses Table from Workwize API

This script fetches warehouse data from the Workwize API and populates the PostgreSQL
warehouses table. No PII scrubbing needed as warehouses are business locations.

Usage:
    python populate_warehouses.py
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


def fetch_warehouses():
    """Fetch all warehouses from Workwize API with pagination."""
    all_warehouses = []
    page = 1
    
    headers = {
        'Authorization': f'Bearer {WORKWIZE_KEY}',
        'Accept': 'application/json'
    }
    
    while True:
        url = f'{WORKWIZE_BASE_URL}/warehouses?page={page}'
        print(f"Fetching page {page} from {url}...")
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            if 'data' in data:
                warehouses = data['data']
            elif 'value' in data:
                warehouses = data['value']
            else:
                warehouses = [data]
            
            # Add to collection
            all_warehouses.extend(warehouses)
            
            # Check pagination info
            meta = data.get('meta', {})
            links = data.get('links', {})
            
            current_page = meta.get('current_page', page)
            last_page = meta.get('last_page')
            total = meta.get('total', 0)
            
            print(f"  Page {current_page}: Fetched {len(warehouses)} warehouses (Total so far: {len(all_warehouses)}/{total})")
            
            # Check if there's a next page
            if not links.get('next') or (last_page and current_page >= last_page):
                break
            
            page += 1
        else:
            # If it's just an array, no pagination
            all_warehouses = data
            break
    
    print(f"\n✅ Fetched {len(all_warehouses)} total warehouses")
    return all_warehouses


def transform_warehouse(warehouse):
    """Transform API warehouse data to database format."""
    # Extract basic data
    warehouse_id = str(warehouse.get('id', ''))
    
    # Warehouse name
    name = warehouse.get('name') or f"Warehouse {warehouse_id}"
    
    # Warehouse code
    code = warehouse.get('code') or warehouse.get('warehouse_code')
    
    # Address ID - may need to look up from addresses table
    address_id = None
    if warehouse.get('address'):
        if isinstance(warehouse['address'], dict):
            addr_id = warehouse['address'].get('id')
            if addr_id:
                address_id = str(addr_id)
        else:
            address_id = str(warehouse['address'])
    elif warehouse.get('address_id'):
        address_id = str(warehouse['address_id'])
    
    # Capacity
    capacity = warehouse.get('capacity') or warehouse.get('max_capacity')
    if capacity:
        try:
            capacity = int(capacity)
        except:
            capacity = None
    
    # Status
    status = warehouse.get('status') or 'active'
    
    # Type
    warehouse_type = warehouse.get('type') or warehouse.get('warehouse_provider')
    
    # Timestamps
    created_at = datetime.now()
    if warehouse.get('created_at') or warehouse.get('createdAt'):
        date_str = warehouse.get('created_at') or warehouse.get('createdAt')
        try:
            created_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    updated_at = datetime.now()
    if warehouse.get('updated_at') or warehouse.get('updatedAt'):
        date_str = warehouse.get('updated_at') or warehouse.get('updatedAt')
        try:
            updated_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    return (
        warehouse_id,
        name,
        code,
        address_id,
        capacity,
        status,
        warehouse_type,
        created_at,
        updated_at
    )


def populate_warehouses(warehouses):
    """Insert warehouses into PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Transform all warehouses
        warehouse_data = [transform_warehouse(warehouse) for warehouse in warehouses]
        
        # Insert query with ON CONFLICT to handle duplicates
        insert_query = """
            INSERT INTO warehouses (
                id, name, code, "addressId", capacity, status,
                type, "createdAt", "updatedAt"
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                code = EXCLUDED.code,
                "addressId" = EXCLUDED."addressId",
                capacity = EXCLUDED.capacity,
                status = EXCLUDED.status,
                type = EXCLUDED.type,
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        # Execute batch insert
        execute_values(cursor, insert_query, warehouse_data)
        
        conn.commit()
        print(f"✅ Successfully inserted/updated {len(warehouse_data)} warehouses")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM warehouses")
        total = cursor.fetchone()[0]
        print(f"📊 Total warehouses in database: {total}")
        
        cursor.execute("SELECT status, COUNT(*) FROM warehouses GROUP BY status ORDER BY COUNT(*) DESC")
        status_counts = cursor.fetchall()
        if status_counts:
            print("\n📈 Warehouses by status:")
            for status, count in status_counts:
                print(f"  {status or 'Unknown'}: {count}")
        
        cursor.execute("SELECT type, COUNT(*) FROM warehouses WHERE type IS NOT NULL GROUP BY type ORDER BY COUNT(*) DESC")
        type_counts = cursor.fetchall()
        if type_counts:
            print("\n🏭 Warehouses by type:")
            for wh_type, count in type_counts:
                print(f"  {wh_type}: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting warehouses: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function."""
    print("=" * 60)
    print("Workwize Warehouse Population Script")
    print("=" * 60)
    
    # Validate environment variables
    if not WORKWIZE_KEY:
        print("❌ Error: WORKWIZE_KEY not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Fetch warehouses from API
        warehouses = fetch_warehouses()
        
        if not warehouses:
            print("⚠️  No warehouses found in API response")
            return
        
        # Populate database
        populate_warehouses(warehouses)
        
        print("\n✅ Warehouse population complete!")
        
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
