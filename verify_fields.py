#!/usr/bin/env python3
"""Quick script to verify v2.0 fields are populated"""
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

project_root = Path(__file__).parent
load_dotenv(project_root / '.env')

DATABASE_URL = os.getenv('DATABASE_URL')

def verify_fields():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Employee fields
    print("=" * 60)
    print("EMPLOYEE NEW FIELDS")
    print("=" * 60)
    cur.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT(team) as with_team,
            COUNT("foreignId") as with_foreign_id,
            COUNT("registrationStatus") as with_reg_status,
            COUNT("isDeactivated") as with_is_deactivated,
            COUNT("userId") as with_user_id
        FROM employees
    ''')
    row = cur.fetchone()
    print(f"Total employees: {row[0]}")
    print(f"With team: {row[1]} ({row[1]/row[0]*100:.1f}%)")
    print(f"With foreignId: {row[2]} ({row[2]/row[0]*100:.1f}%)")
    print(f"With registrationStatus: {row[3]} ({row[3]/row[0]*100:.1f}%)")
    print(f"With isDeactivated: {row[4]} ({row[4]/row[0]*100:.1f}%)")
    print(f"With userId: {row[5]} ({row[5]/row[0]*100:.1f}%)")
    
    # Asset fields
    print("\n" + "=" * 60)
    print("ASSET NEW/RENAMED FIELDS")
    print("=" * 60)
    cur.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT("serialCode") as with_serial,
            COUNT("invoicePrice") as with_invoice_price,
            COUNT("invoiceCurrency") as with_invoice_currency,
            COUNT("warehouseStatus") as with_warehouse_status,
            COUNT(condition) as with_condition,
            COUNT(tags) as with_tags,
            COUNT("externalReference") as with_external_ref
        FROM assets
    ''')
    row = cur.fetchone()
    print(f"Total assets: {row[0]}")
    print(f"With serialCode: {row[1]} ({row[1]/row[0]*100:.1f}%)")
    print(f"With invoicePrice: {row[2]} ({row[2]/row[0]*100:.1f}%)")
    print(f"With invoiceCurrency: {row[3]} ({row[3]/row[0]*100:.1f}%)")
    print(f"With warehouseStatus: {row[4]} ({row[4]/row[0]*100:.1f}%)")
    print(f"With condition: {row[5]} ({row[5]/row[0]*100:.1f}%)")
    print(f"With tags: {row[6]} ({row[6]/row[0]*100:.1f}%)")
    print(f"With externalReference: {row[7]} ({row[7]/row[0]*100:.1f}%)")
    
    # Order fields
    print("\n" + "=" * 60)
    print("ORDER NEW FIELDS")
    print("=" * 60)
    cur.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT("poNumber") as with_po_number,
            COUNT("totalProducts") as with_total_products,
            COUNT(receiver) as with_receiver,
            COUNT("receiverType") as with_receiver_type,
            COUNT("expressDelivery") as with_express_delivery,
            COUNT("shippingInfo") as with_shipping_info
        FROM orders
    ''')
    row = cur.fetchone()
    print(f"Total orders: {row[0]}")
    print(f"With poNumber: {row[1]} ({row[1]/row[0]*100:.1f}%)")
    print(f"With totalProducts: {row[2]} ({row[2]/row[0]*100:.1f}%)")
    print(f"With receiver: {row[3]} ({row[3]/row[0]*100:.1f}%)")
    print(f"With receiverType: {row[4]} ({row[4]/row[0]*100:.1f}%)")
    print(f"With expressDelivery: {row[5]} ({row[5]/row[0]*100:.1f}%)")
    print(f"With shippingInfo: {row[6]} ({row[6]/row[0]*100:.1f}%)")
    
    # Sample data
    print("\n" + "=" * 60)
    print("SAMPLE DATA")
    print("=" * 60)
    cur.execute('SELECT id, "serialCode", "invoicePrice", "invoiceCurrency" FROM assets WHERE "serialCode" IS NOT NULL LIMIT 3')
    print("\nAsset samples:")
    for row in cur.fetchall():
        print(f"  ID {row[0]}: serial={row[1]}, price={row[2]}, currency={row[3]}")
    
    cur.execute('SELECT id, team, "foreignId", "registrationStatus" FROM employees WHERE team IS NOT NULL LIMIT 3')
    print("\nEmployee samples:")
    for row in cur.fetchall():
        print(f"  ID {row[0]}: team={row[1]}, foreignId={row[2]}, regStatus={row[3]}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    verify_fields()
