import psycopg2

conn = psycopg2.connect('postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db')
cur = conn.cursor()

# Check warehouses
cur.execute('SELECT COUNT(*) FROM warehouses')
print(f'Total warehouses: {cur.fetchone()[0]}')

cur.execute('''
    SELECT w.id, w.name, w.code, a.country 
    FROM warehouses w 
    LEFT JOIN addresses a ON w."addressId" = a.id 
    LIMIT 5
''')
print('\nSample warehouses:')
for row in cur.fetchall():
    print(f'  ID: {row[0]}, Name: {row[1]}, Code: {row[2]}, Country: {row[3]}')

# Check assets with warehouse/office IDs
cur.execute('SELECT COUNT(*) FROM assets WHERE "warehouseId" IS NOT NULL')
wh_count = cur.fetchone()[0]
print(f'\nAssets with warehouseId: {wh_count}')

cur.execute('SELECT COUNT(*) FROM assets WHERE "officeId" IS NOT NULL')
off_count = cur.fetchone()[0]
print(f'Assets with officeId: {off_count}')

if wh_count > 0:
    cur.execute('SELECT id, name, "serialNumber", "warehouseId" FROM assets WHERE "warehouseId" IS NOT NULL LIMIT 3')
    print('\nSample assets in warehouses:')
    for row in cur.fetchall():
        print(f'  Asset: {row[2]} - {row[1]}, Warehouse ID: {row[3]}')

if off_count > 0:
    cur.execute('SELECT id, name, "serialNumber", "officeId" FROM assets WHERE "officeId" IS NOT NULL LIMIT 3')
    print('\nSample assets in offices:')
    for row in cur.fetchall():
        print(f'  Asset: {row[2]} - {row[1]}, Office ID: {row[3]}')

conn.close()
