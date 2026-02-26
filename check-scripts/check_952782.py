import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute('SELECT id, "addressId" FROM employees WHERE id = %s', ('952782',))
row = cur.fetchone()
print(f"Employee 952782: id={row[0]}, addressId={row[1]}")

conn.close()
