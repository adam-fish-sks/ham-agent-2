import psycopg2

conn = psycopg2.connect('postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db')
cur = conn.cursor()

# Get asset details
cur.execute('''
    SELECT 
        a.id, 
        a.name, 
        a."serialNumber", 
        a.status, 
        a."assignedToId", 
        a."warehouseId", 
        a."officeId"
    FROM assets a
    WHERE a."serialNumber" = %s
''', ('LQWQG0VMH3',))

asset = cur.fetchone()

if not asset:
    print("Asset not found!")
    conn.close()
    exit()

asset_id, name, serial, status, assigned_to_id, warehouse_id, office_id = asset

print(f'Asset: {serial}')
print(f'  Name: {name}')
print(f'  Status: {status}')
print(f'  AssignedToId: {assigned_to_id}')
print(f'  WarehouseId: {warehouse_id}')
print(f'  OfficeId: {office_id}')

# Check employee address if assigned
if assigned_to_id:
    cur.execute('''
        SELECT e."firstName", e."lastName", e."addressId", a.country, a.city
        FROM employees e
        LEFT JOIN addresses a ON e."addressId" = a.id
        WHERE e.id = %s
    ''', (assigned_to_id,))
    
    emp = cur.fetchone()
    if emp:
        print(f'\nAssigned to: {emp[0]} {emp[1]}')
        print(f'  Employee AddressId: {emp[2]}')
        print(f'  Address Country: {emp[3]}')
        print(f'  Address City: {emp[4]}')

# Check warehouse address if in warehouse
if warehouse_id:
    cur.execute('''
        SELECT w.name, w.code, w."addressId", a.country, a.city
        FROM warehouses w
        LEFT JOIN addresses a ON w."addressId" = a.id
        WHERE w.id = %s
    ''', (warehouse_id,))
    
    wh = cur.fetchone()
    if wh:
        print(f'\nWarehouse: {wh[0]} ({wh[1]})')
        print(f'  Warehouse AddressId: {wh[2]}')
        print(f'  Address Country: {wh[3]}')
        print(f'  Address City: {wh[4]}')

conn.close()
