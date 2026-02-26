import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Check how many employees have addressId
cursor.execute('SELECT COUNT(*) FROM employees WHERE "addressId" IS NOT NULL')
emp_with_addr = cursor.fetchone()[0]
print(f'Employees with addressId: {emp_with_addr}')

# Check unique address IDs referenced by employees
cursor.execute('SELECT COUNT(DISTINCT "addressId") FROM employees WHERE "addressId" IS NOT NULL')
unique_addr = cursor.fetchone()[0]
print(f'Unique address IDs from employees: {unique_addr}')

# Check how many of those addresses exist in the addresses table
cursor.execute("""
    SELECT COUNT(DISTINCT e."addressId") 
    FROM employees e 
    WHERE e."addressId" IS NOT NULL 
    AND EXISTS (SELECT 1 FROM addresses a WHERE a.id = e."addressId")
""")
existing_addr = cursor.fetchone()[0]
print(f'Address IDs that exist in addresses table: {existing_addr}')

# Sample a few addresses to see their structure
cursor.execute("""
    SELECT a.id, a.country, a.city, a."postalCode"
    FROM addresses a
    WHERE a.id IN (
        SELECT DISTINCT e."addressId" 
        FROM employees e 
        WHERE e."addressId" IS NOT NULL 
        LIMIT 5
    )
""")
print(f'\nSample employee addresses:')
for row in cursor.fetchall():
    print(f'  ID: {row[0]}, Country: {row[1]}, City: {row[2]}, PostalCode: {row[3]}')

cursor.close()
conn.close()
