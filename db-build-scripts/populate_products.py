"""
Populate Products Table from Workwize API

This script fetches product data from the Workwize API and populates the PostgreSQL
products table. No PII scrubbing needed as products are catalog items.

Usage:
    python populate_products.py
"""

import os
import sys
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configuration
WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
WORKWIZE_BASE_URL = 'https://prod-back.goworkwize.com/api/public'


def strip_html(text):
    """Strip HTML tags from text."""
    if not text:
        return None
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()


def fetch_products():
    """Fetch all products from Workwize API with pagination."""
    all_products = []
    page = 1
    
    headers = {
        'Authorization': f'Bearer {WORKWIZE_KEY}',
        'Accept': 'application/json'
    }
    
    while True:
        url = f'{WORKWIZE_BASE_URL}/products?page={page}'
        print(f"Fetching page {page} from {url}...")
        
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            if 'data' in data:
                products = data['data']
            elif 'value' in data:
                products = data['value']
            else:
                products = [data]
            
            # Add to collection
            all_products.extend(products)
            
            # Check pagination info
            meta = data.get('meta', {})
            links = data.get('links', {})
            
            current_page = meta.get('current_page', page)
            last_page = meta.get('last_page')
            total = meta.get('total', 0)
            
            print(f"  Page {current_page}: Fetched {len(products)} products (Total so far: {len(all_products)}/{total})")
            
            # Check if there's a next page
            if not links.get('next') or (last_page and current_page >= last_page):
                break
            
            page += 1
        else:
            # If it's just an array, no pagination
            all_products = data
            break
    
    print(f"\n✅ Fetched {len(all_products)} total products")
    return all_products


def transform_product(product):
    """Transform API product data to database format."""
    # Extract basic data
    product_id = str(product.get('id', ''))
    
    # Product name
    name = product.get('name') or f"Product {product_id}"
    
    # SKU
    sku = product.get('sku') or product.get('article_code') or product.get('ean')
    
    # Category
    category = None
    category_data = product.get('category')
    if category_data:
        if isinstance(category_data, dict):
            category = category_data.get('name')
        else:
            category = str(category_data)
    
    # Description - strip HTML
    description = None
    desc_raw = product.get('description') or product.get('short_description')
    if desc_raw:
        description = strip_html(desc_raw)
        if description and len(description) > 5000:  # Truncate if too long
            description = description[:4997] + '...'
    
    # Manufacturer - extract from name or attributes
    manufacturer = product.get('manufacturer') or product.get('brand')
    if not manufacturer and name:
        # Try to extract first word from name (often the brand)
        parts = name.split(',')
        if parts:
            manufacturer = parts[0].strip()
    
    # Model
    model = product.get('model')
    
    # Price and currency
    price = None
    currency = None
    
    # Try different price fields
    price_val = product.get('price') or product.get('buy_price') or product.get('rental_price')
    if price_val:
        try:
            price = Decimal(str(price_val))
        except:
            pass
    
    # Get currency
    currency_data = product.get('currency')
    if currency_data:
        if isinstance(currency_data, dict):
            currency = currency_data.get('name') or currency_data.get('code')
        else:
            currency = str(currency_data)
    
    # Status
    status = product.get('status') or 'active'
    
    # Stock quantity
    stock_quantity = None
    stock_val = product.get('stock_quantity') or product.get('quantity')
    if stock_val:
        try:
            stock_quantity = int(stock_val)
        except:
            pass
    
    # Timestamps
    created_at = datetime.now()
    if product.get('created_at') or product.get('createdAt'):
        date_str = product.get('created_at') or product.get('createdAt')
        try:
            created_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    updated_at = datetime.now()
    if product.get('updated_at') or product.get('updatedAt'):
        date_str = product.get('updated_at') or product.get('updatedAt')
        try:
            updated_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
    
    return (
        product_id,
        name,
        sku,
        category,
        description,
        manufacturer,
        model,
        price,
        currency,
        status,
        stock_quantity,
        created_at,
        updated_at
    )


def populate_products(products):
    """Insert products into PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Transform all products
        product_data = [transform_product(product) for product in products]
        
        # First, handle duplicate SKUs by appending product ID
        seen_skus = {}
        cleaned_data = []
        for row in product_data:
            product_id, name, sku, *rest = row
            if sku:
                if sku in seen_skus:
                    # Append product ID to make SKU unique
                    sku = f"{sku}-{product_id}"
                else:
                    seen_skus[sku] = True
            cleaned_data.append((product_id, name, sku, *rest))
        
        # Insert query with ON CONFLICT to handle duplicates
        insert_query = """
            INSERT INTO products (
                id, name, sku, category, description, manufacturer,
                model, price, currency, status, "stockQuantity",
                "createdAt", "updatedAt"
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                sku = EXCLUDED.sku,
                category = EXCLUDED.category,
                description = EXCLUDED.description,
                manufacturer = EXCLUDED.manufacturer,
                model = EXCLUDED.model,
                price = EXCLUDED.price,
                currency = EXCLUDED.currency,
                status = EXCLUDED.status,
                "stockQuantity" = EXCLUDED."stockQuantity",
                "updatedAt" = EXCLUDED."updatedAt"
        """
        
        # Execute batch insert
        execute_values(cursor, insert_query, cleaned_data)
        
        conn.commit()
        print(f"✅ Successfully inserted/updated {len(cleaned_data)} products")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM products")
        total = cursor.fetchone()[0]
        print(f"📊 Total products in database: {total}")
        
        cursor.execute("SELECT category, COUNT(*) FROM products WHERE category IS NOT NULL GROUP BY category ORDER BY COUNT(*) DESC LIMIT 10")
        category_counts = cursor.fetchall()
        if category_counts:
            print("\n📈 Top 10 product categories:")
            for category, count in category_counts:
                print(f"  {category}: {count}")
        
        cursor.execute("SELECT manufacturer, COUNT(*) FROM products WHERE manufacturer IS NOT NULL GROUP BY manufacturer ORDER BY COUNT(*) DESC LIMIT 10")
        manufacturer_counts = cursor.fetchall()
        if manufacturer_counts:
            print("\n🏭 Top 10 manufacturers:")
            for manufacturer, count in manufacturer_counts:
                print(f"  {manufacturer}: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting products: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function."""
    print("=" * 60)
    print("Workwize Product Population Script")
    print("=" * 60)
    
    # Validate environment variables
    if not WORKWIZE_KEY:
        print("❌ Error: WORKWIZE_KEY not found in environment variables")
        sys.exit(1)
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    try:
        # Fetch products from API
        products = fetch_products()
        
        if not products:
            print("⚠️  No products found in API response")
            return
        
        # Populate database
        populate_products(products)
        
        print("\n✅ Product population complete!")
        
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
