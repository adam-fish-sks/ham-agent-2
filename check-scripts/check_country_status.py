import psycopg2

conn = psycopg2.connect('postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db')
cur = conn.cursor()

# Check employees with addresses
cur.execute('SELECT COUNT(*) FROM employees WHERE "addressId" IS NOT NULL')
emp_with_addr = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM employees')
total_emp = cur.fetchone()[0]

# Check assigned assets
cur.execute('SELECT COUNT(*) FROM assets WHERE "assignedToId" IS NOT NULL')
assigned_assets = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM assets')
total_assets = cur.fetchone()[0]

print(f'Employees with addresses: {emp_with_addr}/{total_emp} ({emp_with_addr*100//total_emp if total_emp > 0 else 0}%)')
print(f'Assets assigned to employees: {assigned_assets}/{total_assets}')
print(f'\nEstimated assets that can show country: ~{emp_with_addr * assigned_assets // total_emp if total_emp > 0 else 0}')

# Check sample assets with country data
cur.execute('''
    SELECT a.id, a.name, e."firstName", e."lastName", addr.country 
    FROM assets a
    LEFT JOIN employees e ON a."assignedToId" = e.id
    LEFT JOIN addresses addr ON e."addressId" = addr.id
    WHERE a."assignedToId" IS NOT NULL
    LIMIT 5
''')

print('\nSample assets with country data:')
for row in cur.fetchall():
    asset_id, asset_name, first_name, last_name, country = row
    country_display = country if country else 'No country'
    print(f'  {asset_name}: {first_name} {last_name} - {country_display}')

cur.close()
conn.close()
