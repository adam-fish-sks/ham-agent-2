#!/usr/bin/env python3
"""Test backend API response for warehouse data"""
import psycopg2
import os
from dotenv import load_dotenv
import json

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Query exactly like Prisma would
cur.execute("""
    SELECT 
        a.id, a."serialCode", a.name, a."warehouseId",
        w.id as w_id, w.name as w_name, w.code as w_code,
        wa.id as addr_id, wa.country as addr_country
    FROM assets a
    LEFT JOIN warehouses w ON a."warehouseId" = w.id
    LEFT JOIN addresses wa ON w."addressId" = wa.id
    WHERE a."serialCode" = 'CR8QCY3'
""")

result = cur.fetchone()

if result:
    print(f"Asset ID: {result[0]}")
    print(f"Serial Code: {result[1]}")
    print(f"Asset Name: {result[2]}")
    print(f"Warehouse ID: {result[3]}")
    print(f"\nWarehouse:")
    print(f"  ID: {result[4]}")
    print(f"  Name: {result[5]}")
    print(f"  Code: {result[6]}")
    print(f"\nWarehouse Address:")
    print(f"  ID: {result[7]}")
    print(f"  Country: {result[8]}")
    
    # Show what backend should return
    print(f"\nBackend should return:")
    print(json.dumps({
        "id": result[0],
        "serialCode": result[1],
        "name": result[2],
        "warehouse": {
            "id": result[4],
            "name": result[5],
            "code": result[6],
            "address": {
                "id": result[7],
                "country": result[8]
            }
        }
    }, indent=2))
else:
    print("Asset not found")

cur.close()
conn.close()
