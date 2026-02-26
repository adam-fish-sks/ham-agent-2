import psycopg2

conn = psycopg2.connect('postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db')
cur = conn.cursor()

cur.execute('''
    SELECT id, name, "serialNumber", status, location, "assignedToId", "warehouseId", "officeId" 
    FROM assets 
    WHERE "serialNumber" = %s
''', ('CR8QCY3',))

row = cur.fetchone()

if row:
    print('Asset CR8QCY3 Found:')
    print(f'  ID: {row[0]}')
    print(f'  Name: {row[1]}')
    print(f'  Serial: {row[2]}')
    print(f'  Status: {row[3]}')
    print(f'  Location: {row[4]}')
    print(f'  AssignedToId: {row[5]}')
    print(f'  WarehouseId: {row[6]}')
    print(f'  OfficeId: {row[7]}')
else:
    print('Asset CR8QCY3 not found in database')

conn.close()
