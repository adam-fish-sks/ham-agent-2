"""
Create addresses for warehouses based on their codes
The warehouse codes appear to be airport codes which can be mapped to locations
"""

import psycopg2
from datetime import datetime

# Mapping of warehouse codes to locations (based on airport codes)
WAREHOUSE_LOCATIONS = {
    'LDW': {'city': 'London', 'country': 'United Kingdom'},  # Likely Heathrow area
    'ER3': {'city': 'Rotterdam', 'country': 'Netherlands'},  # European distribution
    'VEW': {'city': 'Veldhoven', 'country': 'Netherlands'},  # Netherlands location
    'LBZ': {'city': 'Labège', 'country': 'France'},  # France logistics hub
    'LPB': {'city': 'Leipzig', 'country': 'Germany'},  # German logistics hub
    'YYZ': {'city': 'Toronto', 'country': 'Canada'},  # Toronto Pearson Airport
    'SYD': {'city': 'Sydney', 'country': 'Australia'},  # Sydney Airport
    'LPP': {'city': 'Lappeenranta', 'country': 'Finland'},  # Finland
    'MXW': {'city': 'Manassas', 'country': 'United States'},  # Virginia, US
    'SIW': {'city': 'Singapore', 'country': 'Singapore'},  # Singapore
    'SOA': {'city': 'Soacha', 'country': 'Colombia'},  # Colombia
    'CSW': {'city': 'Columbus', 'country': 'United States'},  # US warehouse
    'TYO': {'city': 'Tokyo', 'country': 'Japan'},  # Tokyo
    'DXB': {'city': 'Dubai', 'country': 'United Arab Emirates'},  # Dubai
    'MEX': {'city': 'Mexico City', 'country': 'Mexico'},  # Mexico City
    'MRS': {'city': 'Marseille', 'country': 'France'},  # Marseille, France
    'JER': {'city': 'Jersey', 'country': 'United Kingdom'},  # Jersey
    'IND': {'city': 'Indianapolis', 'country': 'United States'},  # Indianapolis
}

# No corrections needed - all in main dict now
WAREHOUSE_CORRECTIONS = {}

# Apply corrections
WAREHOUSE_LOCATIONS.update(WAREHOUSE_CORRECTIONS)

def create_warehouse_addresses():
    """Create addresses for warehouses and link them"""
    conn = psycopg2.connect('postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db')
    cur = conn.cursor()
    
    try:
        # Get all warehouses
        cur.execute('SELECT id, code FROM warehouses')
        warehouses = cur.fetchall()
        
        print(f"Found {len(warehouses)} warehouses")
        
        updated_count = 0
        created_count = 0
        
        for wh_id, wh_code in warehouses:
            if not wh_code or wh_code not in WAREHOUSE_LOCATIONS:
                print(f"  ⚠️  Unknown warehouse code: {wh_code}")
                continue
            
            location = WAREHOUSE_LOCATIONS[wh_code]
            city = location['city']
            country = location['country']
            
            # Check if address already exists for this city/country
            cur.execute('''
                SELECT id FROM addresses 
                WHERE city = %s AND country = %s
                LIMIT 1
            ''', (city, country))
            
            existing = cur.fetchone()
            
            if existing:
                address_id = existing[0]
                print(f"  ✓ Found existing address for {wh_code} ({city}, {country})")
            else:
                # Create new address
                now = datetime.now()
                cur.execute('''
                    INSERT INTO addresses (id, city, country, "createdAt", "updatedAt")
                    VALUES (gen_random_uuid()::text, %s, %s, %s, %s)
                    RETURNING id
                ''', (city, country, now, now))
                
                address_id = cur.fetchone()[0]
                created_count += 1
                print(f"  ✓ Created address for {wh_code} ({city}, {country})")
            
            # Update warehouse with address ID
            cur.execute('''
                UPDATE warehouses 
                SET "addressId" = %s
                WHERE id = %s
            ''', (address_id, wh_id))
            
            updated_count += 1
        
        conn.commit()
        
        print(f"\n✅ Updated {updated_count} warehouses")
        print(f"✅ Created {created_count} new addresses")
        
        # Show results
        cur.execute('''
            SELECT w.code, w.name, a.city, a.country
            FROM warehouses w
            LEFT JOIN addresses a ON w."addressId" = a.id
            ORDER BY w.code
        ''')
        
        print("\nWarehouse Locations:")
        for row in cur.fetchall():
            code, name, city, country = row
            if city and country:
                print(f"  {code}: {city}, {country}")
            else:
                print(f"  {code}: (no location)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    create_warehouse_addresses()
