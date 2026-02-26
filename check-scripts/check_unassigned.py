import psycopg2

conn = psycopg2.connect('postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db')
cur = conn.cursor()

# Check locations for unassigned assets
cur.execute('SELECT id, name, "serialNumber", location, status FROM assets WHERE "assignedToId" IS NULL LIMIT 15')
rows = cur.fetchall()

print('Sample unassigned assets:')
print(f'Found {len(rows)} unassigned assets\n')
for row in rows:
    asset_id, name, serial, location, status = row
    print(f'{serial}: {status}')
    if location:
        print(f'  Location: {location}')
    else:
        print(f'  Location: (none)')
    print()

conn.close()
