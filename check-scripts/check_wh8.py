import psycopg2

conn = psycopg2.connect('postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db')
cur = conn.cursor()

cur.execute('''
    SELECT w.id, w.code, w."addressId", a.country, a.city
    FROM warehouses w
    LEFT JOIN addresses a ON w."addressId" = a.id
    WHERE w.id = '8'
''')

row = cur.fetchone()
print(f'Warehouse 8 (YYZ - Toronto):')
print(f'  Warehouse ID: {row[0]}')
print(f'  Code: {row[1]}')
print(f'  AddressId: {row[2]}')
print(f'  Country: {row[3]}')
print(f'  City: {row[4]}')

conn.close()
