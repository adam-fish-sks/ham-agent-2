import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute('''
    SELECT 
        a."serialNumber", 
        e."addressId", 
        addr.country 
    FROM assets a 
    LEFT JOIN employees e ON a."assignedToId" = e.id 
    LEFT JOIN addresses addr ON e."addressId" = addr.id 
    WHERE a."serialNumber" = %s
''', ('LQWQG0VMH3',))

row = cur.fetchone()
print(f"Asset: {row[0]}")
print(f"Employee addressId: {row[1]}")
print(f"Country: {row[2]}")

conn.close()
