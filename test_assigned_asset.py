import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Find the asset GY5T5C4
cursor.execute("""
    SELECT 
        a.id,
        a."serialCode",
        a.name,
        a."assignedToId",
        a."warehouseId",
        e.id as emp_id,
        e."firstName",
        e."lastName",
        e."addressId" as emp_address_id,
        addr.id as address_id,
        addr.country,
        addr.city,
        addr."postalCode"
    FROM assets a
    LEFT JOIN employees e ON a."assignedToId" = e.id
    LEFT JOIN addresses addr ON e."addressId" = addr.id
    WHERE a."serialCode" = %s
""", ('GY5T5C4',))

result = cursor.fetchone()

if result:
    print(f'Asset ID: {result[0]}')
    print(f'Serial Code: {result[1]}')
    print(f'Name: {result[2]}')
    print(f'AssignedToId: {result[3]}')
    print(f'WarehouseId: {result[4]}')
    print(f'\nEmployee Details:')
    print(f'  Employee ID: {result[5]}')
    print(f'  Employee Name: {result[6]} {result[7]}')
    print(f'  Employee AddressId: {result[8]}')
    print(f'\nAddress Details:')
    print(f'  Address ID: {result[9]}')
    print(f'  Country: {result[10]}')
    print(f'  City: {result[11]}')
    print(f'  Postal Code: {result[12]}')
else:
    print('Asset not found')

cursor.close()
conn.close()
