"""
Populate Employees Table from Workwize API

This script fetches employee data from the Workwize API and populates the PostgreSQL
employees table with PII scrubbing applied according to the security guidelines.

Usage:
    python populate_employees.py
"""

import os
import sys
import re
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from dotenv import load_dotenv
import time
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Configuration
WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
WORKWIZE_BASE_URL = 'https://prod-back.goworkwize.com/api/public'

# PII Scrubbing Functions
def redact_name(name):
    """Redact name to first letter + asterisks."""
    if not name or len(name) == 0:
        return "***"
    return f"{name[0]}***"


def anonymize_email(email):
    """Anonymize email to first letter + *** + @domain."""
    if not email or '@' not in email:
        return "***@***.com"
    
    local, domain = email.split('@', 1)
    if len(local) == 0:
        return f"***@{domain}"
    
    return f"{local[0]}***@{domain}"


def fetch_employee_address(employee_id):
    """Fetch address ID for a specific employee."""
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
        
        # Extract address ID
        if isinstance(data, dict) and data.get('data'):
            address_data = data['data']
            if address_data and address_data.get('id'):
                return str(address_data['id'])
        
        return None
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response and e.response.status_code == 404:
            return None
        return None
    finally:
        # Small delay to avoid overwhelming API (10 workers * 0.01s = ~100 req/sec max)
        time.sleep(0.01)


def fetch_employees():
    """Fetch all employees from Workwize API with pagination."""
    all_employees = []
    page = 1
    
    headers = {
        'Authorization': f'Bearer {WORKWIZE_KEY}',
        'Accept': 'application/json'
    }
    
    while True:
        url = f'{WORKWIZE_BASE_URL}/employees?page={page}'
        print(f"Fetching page {page} from {url}...")
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            if 'data' in data:
                employees = data['data']
            elif 'value' in data:
                employees = data['value']
            else:
                employees = [data]
            
            # Add to collection
            all_employees.extend(employees)
            
            # Check pagination info
            meta = data.get('meta', {})
            links = data.get('links', {})
            
            current_page = meta.get('current_page', page)
            last_page = meta.get('last_page')
            total = meta.get('total', 0)
            
            print(f"  Page {current_page}: Fetched {len(employees)} employees (Total so far: {len(all_employees)}/{total})")
            
            # Check if there's a next page
            if not links.get('next') or (last_page and current_page >= last_page):
                break
            
            page += 1
        else:
            # If it's just an array, no pagination
            all_employees = data
            break
    
    print(f"\n✅ Fetched {len(all_employees)} total employees")
    return all_employees


def transform_employee(employee, address_id=None):
    """Transform API employee data to database format with PII scrubbing."""
    # Extract basic data
    employee_id = str(employee.get('id', ''))
    
    # PII SCRUBBING - Names
    first_name_raw = employee.get('first_name') or employee.get('firstName') or ''
    last_name_raw = employee.get('last_name') or employee.get('lastName') or ''
    email_raw = employee.get('email') or ''
    
    first_name = redact_name(first_name_raw)
    last_name = redact_name(last_name_raw)
    email = anonymize_email(email_raw)
    
    # Department - extract name from dict
    department = None
    if employee.get('department'):
        if isinstance(employee['department'], dict):
            department = employee['department'].get('name')
        else:
            department = str(employee['department'])
    elif employee.get('team'):
        department = employee.get('team')
    
    # Role - extract from original_role
    role = None
    if employee.get('original_role'):
        if isinstance(employee['original_role'], dict):
            role = employee['original_role'].get('display_name') or employee['original_role'].get('name')
        else:
            role = str(employee['original_role'])
    
    # Status - based on isDeactivated flag
    status = 'inactive' if employee.get('isDeactivated') else 'active'
    
    # Job title
    job_title = employee.get('job_title') or employee.get('jobTitle')
    
    # Manager ID
    manager_id = None
    if employee.get('manager_id'):
        manager_id = str(employee['manager_id'])
    elif employee.get('managerId'):
        manager_id = str(employee['managerId'])
    
    # Office ID
    office_id = None
    if employee.get('office'):
        if isinstance(employee['office'], dict):
            off_id = employee['office'].get('id')
            if off_id:
                office_id = str(off_id)
        else:
            office_id = str(employee['office'])
    elif employee.get('office_id'):
        office_id = str(employee['office_id'])
    elif employee.get('officeId'):
        office_id = str(employee['officeId'])
    
    # Start date
    start_date = None
    if employee.get('start_date') or employee.get('startDate') or employee.get('created_at'):
        date_str = employee.get('start_date') or employee.get('startDate') or employee.get('created_at')
        try:
            start_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    # End date
    end_date = None
    if employee.get('end_date') or employee.get('endDate'):
        date_str = employee.get('end_date') or employee.get('endDate')
        try:
            end_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    # Timestamps
    created_at = datetime.now()
    if employee.get('created_at') or employee.get('createdAt'):
        date_str = employee.get('created_at') or employee.get('createdAt')
        try:
            created_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    updated_at = datetime.now()
    if employee.get('updated_at') or employee.get('updatedAt'):
        date_str = employee.get('updated_at') or employee.get('updatedAt')
        try:
            updated_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    return (
        employee_id,
        first_name,
        last_name,
        email,
        department,
        role,
        status,
        job_title,
        manager_id,
        office_id,
        address_id,
        start_date,
        end_date,
        created_at,
        updated_at
    )


def fetch_employee_with_address(employee):
    """Fetch address for a single employee."""
    employee_id = employee.get('id')
    address_id = None
    
    if employee_id:
        address_id = fetch_employee_address(employee_id)
    
    return transform_employee(employee, address_id)


def populate_employees(employees):
    """Insert employees into PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Get all existing address IDs from database
        cursor.execute("SELECT id FROM addresses")
        existing_address_ids = {str(row[0]) for row in cursor.fetchall()}
        print(f"\n✅ Found {len(existing_address_ids)} addresses in database")
        
        # Transform all employees with address data using parallel processing
        employee_data = []
        print("\nFetching address data for employees (parallel processing)...")
        
        # Use ThreadPoolExecutor for concurrent API calls
        max_workers = 10  # Concurrent requests
        batch_size = 100  # Progress update frequency
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_employee = {executor.submit(fetch_employee_with_address, emp): emp for emp in employees}
            
            completed = 0
            for future in as_completed(future_to_employee):
                try:
                    result = future.result()
                    employee_data.append(result)
                    completed += 1
                    
                    if completed % batch_size == 0 or completed == len(employees):
                        print(f"  Progress: {completed}/{len(employees)} ({completed*100//len(employees)}%)")
                except Exception as e:
                    emp = future_to_employee[future]
                    print(f"  ⚠️  Error processing employee {emp.get('id')}: {e}")
                    # Add employee without address on error
                    employee_data.append(transform_employee(emp, None))
                    completed += 1
        
        print(f"\n✅ Fetched address data for {len(employee_data)} employees")
        
        # Filter out invalid address IDs (those not in the addresses table)
        filtered_employee_data = []
        invalid_address_count = 0
        for emp_tuple in employee_data:
            # emp_tuple is (id, firstName, lastName, ..., addressId, ...)
            # addressId is at index 10
            address_id = emp_tuple[10]
            if address_id is None or str(address_id) in existing_address_ids:
                filtered_employee_data.append(emp_tuple)
            else:
                # Set addressId to None for employees with non-existent addresses
                emp_list = list(emp_tuple)
                emp_list[10] = None
                filtered_employee_data.append(tuple(emp_list))
                invalid_address_count += 1
        
        if invalid_address_count > 0:
            print(f"⚠️  {invalid_address_count} employees have address IDs not in the addresses table (set to NULL)")
        
        # Insert query with ON CONFLICT to handle duplicates
        insert_query = """
            INSERT INTO employees (
                id, "firstName", "lastName", email, department, role,
                status, "jobTitle", "managerId", "officeId", "addressId",
                "startDate", "endDate", "createdAt", "updatedAt"
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                "firstName" = EXCLUDED."firstName",
                "lastName" = EXCLUDED."lastName",
                email = EXCLUDED.email,
                department = EXCLUDED.department,
                role = EXCLUDED.role,
                status = EXCLUDED.status,
                "jobTitle" = EXCLUDED."jobTitle",
                "managerId" = EXCLUDED."managerId",
                "officeId" = EXCLUDED."officeId",
                "addressId" = EXCLUDED."addressId",
                "startDate" = EXCLUDED."startDate",
                "endDate" = EXCLUDED."endDate",
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        # Execute batch insert with filtered data
        execute_values(cursor, insert_query, filtered_employee_data)
        
        conn.commit()
        print(f"✅ Successfully inserted/updated {len(filtered_employee_data)} employees")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM employees")
        total = cursor.fetchone()[0]
        print(f"📊 Total employees in database: {total}")
        
        cursor.execute("SELECT status, COUNT(*) FROM employees GROUP BY status ORDER BY COUNT(*) DESC")
        status_counts = cursor.fetchall()
        print("\n📈 Employees by status:")
        for status, count in status_counts:
            print(f"  {status or 'Unknown'}: {count}")
        
        cursor.execute("SELECT department, COUNT(*) FROM employees WHERE department IS NOT NULL GROUP BY department ORDER BY COUNT(*) DESC LIMIT 10")
        dept_counts = cursor.fetchall()
        print("\n📈 Top 10 departments:")
        for dept, count in dept_counts:
            print(f"  {dept}: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting employees: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function."""
    print("=" * 60)
    print("Workwize Employee Population Script")
    print("=" * 60)
    
    # Validate environment variables
    if not WORKWIZE_KEY:
        print("❌ Error: WORKWIZE_KEY not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Fetch employees from API
        employees = fetch_employees()
        
        if not employees:
            print("⚠️  No employees found in API response")
            return
        
        # Populate database
        populate_employees(employees)
        
        print("\n✅ Employee population complete!")
        print("\n⚠️  REMINDER: All PII has been scrubbed:")
        print("  - Names: Redacted to first letter + ***")
        print("  - Emails: Anonymized to first letter + ***@domain")
        
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
