"""
Populate Offboards Table from Workwize API

This script fetches offboard data from the Workwize API and populates the PostgreSQL
offboards table. PII scrubbing applied to employee names and contact information.

Usage:
    python populate_offboards.py
"""

import os
import sys
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from dotenv import load_dotenv
import re
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Configuration
WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
WORKWIZE_BASE_URL = 'https://prod-back.goworkwize.com/api/public'


def scrub_pii_text(text):
    """Scrub PII from text fields (emails, phone numbers, addresses)."""
    if not text:
        return None
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
    
    # Remove phone numbers (various formats)
    text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', '[PHONE_REDACTED]', text)
    
    # Remove street addresses (lines with numbers and street keywords)
    text = re.sub(r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Court|Ct|Circle|Cir)\b', '[ADDRESS_REDACTED]', text, flags=re.IGNORECASE)
    
    return text.strip()


def fetch_offboards():
    """Fetch all offboards from Workwize API with pagination."""
    all_offboards = []
    page = 1
    
    headers = {
        'Authorization': f'Bearer {WORKWIZE_KEY}',
        'Accept': 'application/json'
    }
    
    while True:
        url = f'{WORKWIZE_BASE_URL}/offboards?page={page}'
        print(f"Fetching page {page} from {url}...")
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            if 'data' in data:
                offboards = data['data']
            elif 'value' in data:
                offboards = data['value']
            else:
                offboards = [data]
            
            # Add to collection
            all_offboards.extend(offboards)
            
            # Check pagination info
            meta = data.get('meta', {})
            links = data.get('links', {})
            
            current_page = meta.get('current_page', page)
            last_page = meta.get('last_page')
            total = meta.get('total', 0)
            
            print(f"  Page {current_page}: Fetched {len(offboards)} offboards (Total so far: {len(all_offboards)}/{total})")
            
            # Check if there's a next page
            if not links.get('next') or (last_page and current_page >= last_page):
                break
            
            page += 1
        else:
            # If it's just an array, no pagination
            all_offboards = data
            break
    
    print(f"\n✅ Fetched {len(all_offboards)} total offboards")
    return all_offboards


def transform_offboard(offboard):
    """Transform API offboard data to database format with PII scrubbing."""
    # Extract basic data
    offboard_id = str(offboard.get('id', ''))
    
    # Employee ID
    employee_id = None
    emp_id = offboard.get('employee_id')
    if emp_id:
        employee_id = str(emp_id)
    
    # Offboard date
    offboard_date = datetime.now()
    date_str = offboard.get('offboard_date') or offboard.get('scheduled_date') or offboard.get('approved_at')
    if date_str:
        try:
            offboard_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    # Reason - scrub PII from reason text
    reason = offboard.get('reason') or offboard.get('type')
    if reason:
        reason = scrub_pii_text(reason)
    
    # Status
    status = offboard.get('status') or 'pending'
    
    # Returned assets
    returned_assets = False
    assets_count = offboard.get('assets_count', 0)
    if assets_count == 0:
        returned_assets = True  # If no assets, consider as returned
    
    # Check if assets were returned based on asset status
    assets = offboard.get('assets', [])
    if assets:
        # If all assets have status indicating return, mark as returned
        all_returned = all(
            asset.get('status') in ['returned', 'received', 'available'] 
            for asset in assets if isinstance(asset, dict)
        )
        if all_returned:
            returned_assets = True
    
    # Notes - scrub PII
    notes = offboard.get('notes') or offboard.get('extra_info')
    if notes:
        notes = scrub_pii_text(notes)
    
    # Processed by
    processed_by = None
    proc_by = offboard.get('processed_by') or offboard.get('approved_by')
    if proc_by:
        processed_by = str(proc_by)
    
    # Timestamps
    created_at = datetime.now()
    if offboard.get('created_at') or offboard.get('createdAt'):
        date_str = offboard.get('created_at') or offboard.get('createdAt')
        try:
            created_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    updated_at = datetime.now()
    if offboard.get('updated_at') or offboard.get('updatedAt'):
        date_str = offboard.get('updated_at') or offboard.get('updatedAt')
        try:
            updated_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    return (
        offboard_id,
        employee_id,
        offboard_date,
        reason,
        status,
        returned_assets,
        notes,
        processed_by,
        created_at,
        updated_at
    )


def populate_offboards(offboards):
    """Insert offboards into PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Get existing employee IDs to validate foreign keys
        cursor.execute("SELECT id FROM employees")
        valid_employee_ids = {row[0] for row in cursor.fetchall()}
        
        # Transform and filter offboards
        offboard_data = []
        skipped = 0
        for offboard in offboards:
            transformed = transform_offboard(offboard)
            employee_id = transformed[1]
            
            # Skip if employee doesn't exist (could be from deleted accounts)
            if employee_id and employee_id not in valid_employee_ids:
                skipped += 1
                continue
            
            offboard_data.append(transformed)
        
        if skipped > 0:
            print(f"⚠️  Skipped {skipped} offboards with invalid employee references")
        
        if not offboard_data:
            print("⚠️  No valid offboards to insert")
            return
        
        # Insert query with ON CONFLICT to handle duplicates
        insert_query = """
            INSERT INTO offboards (
                id, "employeeId", "offboardDate", reason, status,
                "returnedAssets", notes, "processedBy", "createdAt", "updatedAt"
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                "employeeId" = EXCLUDED."employeeId",
                "offboardDate" = EXCLUDED."offboardDate",
                reason = EXCLUDED.reason,
                status = EXCLUDED.status,
                "returnedAssets" = EXCLUDED."returnedAssets",
                notes = EXCLUDED.notes,
                "processedBy" = EXCLUDED."processedBy",
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        # Execute batch insert
        execute_values(cursor, insert_query, offboard_data)
        
        conn.commit()
        print(f"✅ Successfully inserted/updated {len(offboard_data)} offboards")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM offboards")
        total = cursor.fetchone()[0]
        print(f"📊 Total offboards in database: {total}")
        
        cursor.execute("SELECT status, COUNT(*) FROM offboards GROUP BY status ORDER BY COUNT(*) DESC")
        status_counts = cursor.fetchall()
        if status_counts:
            print("\n📈 Offboards by status:")
            for status, count in status_counts:
                print(f"  {status or 'Unknown'}: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM offboards WHERE \"returnedAssets\" = true")
        returned = cursor.fetchone()[0]
        print(f"\n📦 Offboards with returned assets: {returned}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting offboards: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function."""
    print("=" * 60)
    print("Workwize Offboard Population Script")
    print("=" * 60)
    
    # Validate environment variables
    if not WORKWIZE_KEY:
        print("❌ Error: WORKWIZE_KEY not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Fetch offboards from API
        offboards = fetch_offboards()
        
        if not offboards:
            print("⚠️  No offboards found in API response")
            return
        
        # Populate database
        populate_offboards(offboards)
        
        print("\n✅ Offboard population complete!")
        
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
