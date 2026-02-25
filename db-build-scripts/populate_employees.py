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


def transform_employee(employee):
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
        start_date,
        end_date,
        created_at,
        updated_at
    )


def populate_employees(employees):
    """Insert employees into PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Transform all employees
        employee_data = [transform_employee(employee) for employee in employees]
        
        # Insert query with ON CONFLICT to handle duplicates
        insert_query = """
            INSERT INTO employees (
                id, "firstName", "lastName", email, department, role,
                status, "jobTitle", "managerId", "officeId",
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
                "startDate" = EXCLUDED."startDate",
                "endDate" = EXCLUDED."endDate",
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        # Execute batch insert
        execute_values(cursor, insert_query, employee_data)
        
        conn.commit()
        print(f"✅ Successfully inserted/updated {len(employee_data)} employees")
        
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
