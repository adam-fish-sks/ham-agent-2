"""
Populate Assets Table from Workwize API

This script fetches asset data from the Workwize API and populates the PostgreSQL
assets table with PII scrubbing applied according to the security guidelines.

Usage:
    python populate_assets.py
"""

import os
import sys
import re
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
WORKWIZE_BASE_URL = 'https://prod-back.goworkwize.com/api/public'

# PII Scrubbing Functions
def scrub_text(text):
    """Remove emails, phone numbers, SSNs, and credit cards from text."""
    if not text:
        return text
    
    # Email pattern
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
    
    # Phone patterns
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
    text = re.sub(r'\b\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b', '[PHONE_REDACTED]', text)
    
    # SSN pattern
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', text)
    
    # Credit card pattern
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_REDACTED]', text)
    
    return text


def scrub_location(location):
    """Keep only city/state level location data."""
    if not location:
        return None
    
    # Handle dict objects (office/location objects from API)
    if isinstance(location, dict):
        city = location.get('city')
        region = location.get('region') or location.get('state')
        if city and region:
            return f"{city}, {region}"
        elif city:
            return city
        return None
    
    # Handle string locations
    if not isinstance(location, str):
        return None
    
    # Remove street addresses, keep only city/state
    # This is a simplified version - in production you'd parse the address more carefully
    parts = location.split(',')
    if len(parts) > 1:
        # Keep last 2 parts (usually city, state/country)
        return ', '.join(parts[-2:]).strip()
    return location


def fetch_assets():
    """Fetch all assets from Workwize API with pagination."""
    all_assets = []
    page = 1
    
    headers = {
        'Authorization': f'Bearer {WORKWIZE_KEY}',
        'Accept': 'application/json'
    }
    
    while True:
        url = f'{WORKWIZE_BASE_URL}/assets?page={page}'
        print(f"Fetching page {page} from {url}...")
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            if 'data' in data:
                assets = data['data']
            elif 'value' in data:
                assets = data['value']
            else:
                assets = [data]
            
            # Add to collection
            all_assets.extend(assets)
            
            # Check pagination info
            meta = data.get('meta', {})
            links = data.get('links', {})
            
            current_page = meta.get('current_page', page)
            last_page = meta.get('last_page')
            total = meta.get('total', 0)
            
            print(f"  Page {current_page}: Fetched {len(assets)} assets (Total so far: {len(all_assets)}/{total})")
            
            # Check if there's a next page
            if not links.get('next') or (last_page and current_page >= last_page):
                break
            
            page += 1
        else:
            # If it's just an array, no pagination
            all_assets = data
            break
    
    print(f"\n✅ Fetched {len(all_assets)} total assets")
    return all_assets


def transform_asset(asset):
    """Transform API asset data to database format with PII scrubbing."""
    # Extract and scrub data
    asset_id = str(asset.get('id', ''))
    asset_tag = asset.get('asset_tag') or asset.get('assetTag') or asset.get('tag') or f"ASSET-{asset_id}"
    name = asset.get('name') or asset.get('product_name') or 'Unknown'
    
    # Category - extract name from dict
    category = None
    if asset.get('category'):
        if isinstance(asset['category'], dict):
            category = asset['category'].get('name')
        else:
            category = str(asset['category'])
    
    status = asset.get('status')
    serial_number = asset.get('serial_number') or asset.get('serialNumber')
    
    # Product ID
    product_id = None
    if asset.get('product'):
        if isinstance(asset['product'], dict):
            prod_id = asset['product'].get('id')
            if prod_id:
                product_id = str(prod_id)
        else:
            product_id = str(asset['product'])
    elif asset.get('product_id'):
        product_id = str(asset['product_id'])
    
    # Assigned employee - ID only from location.location_detail
    assigned_to_id = None
    location_data = asset.get('location')
    if location_data and isinstance(location_data, dict):
        location_type = location_data.get('location_type')
        location_detail = location_data.get('location_detail')
        
        if location_type == 'employee' and location_detail and isinstance(location_detail, dict):
            emp_id = location_detail.get('id')
            if emp_id:
                assigned_to_id = str(emp_id)
    
    # Location - scrubbed to city/state only
    location = None
    if location_data and isinstance(location_data, dict):
        location_detail = location_data.get('location_detail')
        if location_detail and isinstance(location_detail, dict):
            city = location_detail.get('city')
            region = location_detail.get('region') or location_detail.get('state')
            country_data = location_detail.get('country')
            
            parts = []
            if city:
                parts.append(city)
            if region:
                parts.append(region)
            elif country_data and isinstance(country_data, dict):
                parts.append(country_data.get('name'))
            
            if parts:
                location = ', '.join(parts)
    
    # Purchase info
    purchase_date = None
    if asset.get('purchase_date') or asset.get('purchaseDate'):
        date_str = asset.get('purchase_date') or asset.get('purchaseDate')
        try:
            purchase_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    purchase_price = None
    if asset.get('purchase_price') or asset.get('price'):
        try:
            purchase_price = Decimal(str(asset.get('purchase_price') or asset.get('price')))
        except:
            pass
    
    currency = asset.get('currency') or asset.get('invoice_currency')
    
    warranty_expires = None
    if asset.get('warranty_expires') or asset.get('warrantyExpires'):
        date_str = asset.get('warranty_expires') or asset.get('warrantyExpires')
        try:
            warranty_expires = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    # Notes - scrubbed of PII
    notes = scrub_text(asset.get('notes') or asset.get('description'))
    
    # Office/Warehouse IDs - from location if type is office or warehouse
    office_id = None
    warehouse_id = None
    if location_data and isinstance(location_data, dict):
        location_type = location_data.get('location_type')
        location_detail = location_data.get('location_detail')
        
        if location_type == 'office' and location_detail and isinstance(location_detail, dict):
            off_id = location_detail.get('id')
            if off_id:
                office_id = str(off_id)
        elif location_type == 'warehouse' and location_detail and isinstance(location_detail, dict):
            wh_id = location_detail.get('id')
            if wh_id:
                warehouse_id = str(wh_id)
    
    # Timestamps
    created_at = datetime.now()
    if asset.get('created_at') or asset.get('createdAt'):
        date_str = asset.get('created_at') or asset.get('createdAt')
        try:
            created_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    updated_at = datetime.now()
    if asset.get('updated_at') or asset.get('updatedAt'):
        date_str = asset.get('updated_at') or asset.get('updatedAt')
        try:
            updated_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    return (
        asset_id,
        asset_tag,
        name,
        category,
        status,
        serial_number,
        product_id,
        assigned_to_id,
        location,
        purchase_date,
        purchase_price,
        currency,
        warranty_expires,
        notes,
        office_id,
        warehouse_id,
        created_at,
        updated_at
    )


def populate_assets(assets):
    """Insert assets into PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Transform all assets
        asset_data = [transform_asset(asset) for asset in assets]
        
        # Insert query with ON CONFLICT to handle duplicates
        insert_query = """
            INSERT INTO assets (
                id, "assetTag", name, category, status, "serialNumber",
                "productId", "assignedToId", location, "purchaseDate",
                "purchasePrice", currency, "warrantyExpires", notes,
                "officeId", "warehouseId", "createdAt", "updatedAt"
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                "assetTag" = EXCLUDED."assetTag",
                name = EXCLUDED.name,
                category = EXCLUDED.category,
                status = EXCLUDED.status,
                "serialNumber" = EXCLUDED."serialNumber",
                "productId" = EXCLUDED."productId",
                "assignedToId" = EXCLUDED."assignedToId",
                location = EXCLUDED.location,
                "purchaseDate" = EXCLUDED."purchaseDate",
                "purchasePrice" = EXCLUDED."purchasePrice",
                currency = EXCLUDED.currency,
                "warrantyExpires" = EXCLUDED."warrantyExpires",
                notes = EXCLUDED.notes,
                "officeId" = EXCLUDED."officeId",
                "warehouseId" = EXCLUDED."warehouseId",
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        # Execute batch insert
        execute_values(cursor, insert_query, asset_data)
        
        conn.commit()
        print(f"✅ Successfully inserted/updated {len(asset_data)} assets")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM assets")
        total = cursor.fetchone()[0]
        print(f"📊 Total assets in database: {total}")
        
        cursor.execute("SELECT status, COUNT(*) FROM assets GROUP BY status ORDER BY COUNT(*) DESC")
        status_counts = cursor.fetchall()
        print("\n📈 Assets by status:")
        for status, count in status_counts:
            print(f"  {status or 'Unknown'}: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting assets: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function."""
    print("=" * 60)
    print("Workwize Asset Population Script")
    print("=" * 60)
    
    # Validate environment variables
    if not WORKWIZE_KEY:
        print("❌ Error: WORKWIZE_KEY not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Fetch assets from API
        assets = fetch_assets()
        
        if not assets:
            print("⚠️  No assets found in API response")
            return
        
        # Populate database
        populate_assets(assets)
        
        print("\n✅ Asset population complete!")
        
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
