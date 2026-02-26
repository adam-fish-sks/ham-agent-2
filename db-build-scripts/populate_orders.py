"""
Populate Orders Table from Workwize API

This script fetches order data from the Workwize API and populates the PostgreSQL
orders table. No PII scrubbing needed as orders don't contain sensitive personal data
in the database (addresses are stored separately).

Usage:
    python populate_orders.py
"""

import os
import sys
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

# Configuration
WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
WORKWIZE_BASE_URL = 'https://prod-back.goworkwize.com/api/public'


def fetch_orders():
    """Fetch all orders from Workwize API with pagination."""
    all_orders = []
    page = 1
    
    headers = {
        'Authorization': f'Bearer {WORKWIZE_KEY}',
        'Accept': 'application/json'
    }
    
    while True:
        url = f'{WORKWIZE_BASE_URL}/orders?page={page}'
        print(f"Fetching page {page} from {url}...")
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            if 'data' in data:
                orders = data['data']
            elif 'value' in data:
                orders = data['value']
            else:
                orders = [data]
            
            # Add to collection
            all_orders.extend(orders)
            
            # Check pagination info
            meta = data.get('meta', {})
            links = data.get('links', {})
            
            current_page = meta.get('current_page', page)
            last_page = meta.get('last_page')
            total = meta.get('total', 0)
            
            print(f"  Page {current_page}: Fetched {len(orders)} orders (Total so far: {len(all_orders)}/{total})")
            
            # Check if there's a next page
            if not links.get('next') or (last_page and current_page >= last_page):
                break
            
            page += 1
        else:
            # If it's just an array, no pagination
            all_orders = data
            break
    
    print(f"\n✅ Fetched {len(all_orders)} total orders")
    return all_orders


def transform_order(order):
    """Transform API order data to database format."""
    # Extract basic data
    order_id = str(order.get('id', ''))
    
    # Order number
    order_number = order.get('number') or order.get('order_number') or f"ORDER-{order_id}"
    
    # Status
    status = order.get('status') or 'unknown'
    
    # Order date
    order_date = datetime.now()
    if order.get('created_at') or order.get('createdAt'):
        date_str = order.get('created_at') or order.get('createdAt')
        try:
            order_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    # Delivery date
    delivery_date = None
    if order.get('delivery_date') or order.get('deliveryDate'):
        date_str = order.get('delivery_date') or order.get('deliveryDate')
        try:
            delivery_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    # Total amount
    total_amount = None
    if order.get('total_amount') or order.get('buy_subtotal'):
        try:
            amount_val = order.get('total_amount') or order.get('buy_subtotal')
            if amount_val is not None:
                total_amount = Decimal(str(amount_val))
        except:
            pass
    
    # Currency - extract from dict if needed
    currency = None
    currency_data = order.get('currency')
    if currency_data:
        if isinstance(currency_data, dict):
            currency = currency_data.get('name') or currency_data.get('code')
        else:
            currency = str(currency_data)
    
    # Customer ID - from actor/receiver
    customer_id = None
    if order.get('actor'):
        if isinstance(order['actor'], dict):
            cust_id = order['actor'].get('id')
            if cust_id:
                customer_id = str(cust_id)
    elif order.get('customer_id'):
        customer_id = str(order['customer_id'])
    
    # Employee ID - from receiver if type is employee
    employee_id = None
    receiver_type = order.get('receiver_type')
    if receiver_type == 'employee' and order.get('receiver_id'):
        employee_id = str(order['receiver_id'])
    elif order.get('employee_id'):
        employee_id = str(order['employee_id'])
    
    # Warehouse ID
    warehouse_id = None
    if order.get('warehouse'):
        if isinstance(order['warehouse'], dict):
            wh_id = order['warehouse'].get('id')
            if wh_id:
                warehouse_id = str(wh_id)
        else:
            warehouse_id = str(order['warehouse'])
    elif order.get('warehouse_id'):
        warehouse_id = str(order['warehouse_id'])
    
    # Notes
    notes = order.get('notes') or order.get('description')
    
    # New fields from API
    po_number = order.get('po_number') or order.get('poNumber')
    total_products = order.get('total_products') or order.get('totalProducts')
    
    # Receiver info
    receiver = order.get('receiver')
    # receiver_type already fetched above
    
    express_delivery = order.get('express_delivery', False) or order.get('expressDelivery', False)
    
    # Shipping info - store as JSON string
    import json
    shipping_info = None
    if order.get('shipping_info') or order.get('shippingInfo'):
        try:
            shipping_data = order.get('shipping_info') or order.get('shippingInfo')
            shipping_info = json.dumps(shipping_data)
        except:
            pass
    
    # Timestamps
    created_at = order_date  # Use order date as created
    
    updated_at = datetime.now()
    if order.get('updated_at') or order.get('updatedAt'):
        date_str = order.get('updated_at') or order.get('updatedAt')
        try:
            updated_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    return (
        order_id,
        order_number,
        status,
        order_date,
        delivery_date,
        total_amount,
        currency,
        customer_id,
        employee_id,
        warehouse_id,
        notes,
        po_number,
        total_products,
        receiver,
        receiver_type,
        express_delivery,
        shipping_info,
        created_at,
        updated_at
    )


def populate_orders(orders):
    """Insert orders into PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Transform all orders
        order_data = [transform_order(order) for order in orders]
        
        # Insert query with ON CONFLICT to handle duplicates
        insert_query = """
            INSERT INTO orders (
                id, "orderNumber", status, "orderDate", "deliveryDate",
                "totalAmount", currency, "customerId", "employeeId",
                "warehouseId", notes, "poNumber", "totalProducts",
                receiver, "receiverType", "expressDelivery", "shippingInfo",
                "createdAt", "updatedAt"
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                "orderNumber" = EXCLUDED."orderNumber",
                status = EXCLUDED.status,
                "orderDate" = EXCLUDED."orderDate",
                "deliveryDate" = EXCLUDED."deliveryDate",
                "totalAmount" = EXCLUDED."totalAmount",
                currency = EXCLUDED.currency,
                "customerId" = EXCLUDED."customerId",
                "employeeId" = EXCLUDED."employeeId",
                "warehouseId" = EXCLUDED."warehouseId",
                notes = EXCLUDED.notes,
                "poNumber" = EXCLUDED."poNumber",
                "totalProducts" = EXCLUDED."totalProducts",
                receiver = EXCLUDED.receiver,
                "receiverType" = EXCLUDED."receiverType",
                "expressDelivery" = EXCLUDED."expressDelivery",
                "shippingInfo" = EXCLUDED."shippingInfo",
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        # Execute batch insert
        execute_values(cursor, insert_query, order_data)
        
        conn.commit()
        print(f"✅ Successfully inserted/updated {len(order_data)} orders")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM orders")
        total = cursor.fetchone()[0]
        print(f"📊 Total orders in database: {total}")
        
        cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY COUNT(*) DESC")
        status_counts = cursor.fetchall()
        print("\n📈 Orders by status:")
        for status, count in status_counts:
            print(f"  {status or 'Unknown'}: {count}")
        
        cursor.execute("SELECT currency, COUNT(*) FROM orders WHERE currency IS NOT NULL GROUP BY currency ORDER BY COUNT(*) DESC")
        currency_counts = cursor.fetchall()
        print("\n💰 Orders by currency:")
        for currency, count in currency_counts:
            print(f"  {currency}: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting orders: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function."""
    print("=" * 60)
    print("Workwize Order Population Script")
    print("=" * 60)
    
    # Validate environment variables
    if not WORKWIZE_KEY:
        print("❌ Error: WORKWIZE_KEY not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Fetch orders from API
        orders = fetch_orders()
        
        if not orders:
            print("⚠️  No orders found in API response")
            return
        
        # Populate database
        populate_orders(orders)
        
        print("\n✅ Order population complete!")
        
    except requests.RequestException as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"❌ Database Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
