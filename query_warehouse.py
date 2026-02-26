import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Search for asset by serial number and get warehouse info
cur.execute("""
    SELECT a.id, a."assetTag", a.name, a."serialCode", a.status,
           w.id as warehouse_id, w.name as warehouse_name, w.code as warehouse_code,
           wa.city, wa.region, wa.country, wa."postalCode"
    FROM assets a
    LEFT JOIN warehouses w ON a."warehouseId" = w.id
    LEFT JOIN addresses wa ON w."addressId" = wa.id
    WHERE a."serialCode" ILIKE %s
""", ('%CR8QCY3%',))

result = cur.fetchall()
columns = [desc[0] for desc in cur.description]

if result:
    print(f"\nFound asset with serial number CR8QCY3:\n")
    for r in result:
        print(f"Asset ID: {r[0]}")
        print(f"Asset Tag: {r[1]}")
        print(f"Asset Name: {r[2]}")
        print(f"Serial Code: {r[3]}")
        print(f"Status: {r[4]}")
        print(f"\nWarehouse Information:")
        print(f"  Warehouse ID: {r[5]}")
        print(f"  Warehouse Name: {r[6]}")
        print(f"  Warehouse Code: {r[7]}")
        print(f"  Location: {r[8]}, {r[9]}, {r[10]}")
        print(f"  Postal Code: {r[11]}")
else:
    print("No asset found with serial number CR8QCY3")

cur.close()
conn.close()
