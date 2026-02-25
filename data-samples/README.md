# Data Samples

This directory contains **real JSON responses** from the Workwize API endpoints fetched on February 24, 2026.

## Files

- `employees.json` - ✅ Real employee data from GET /employees (58,578 lines)
- `assets.json` - ✅ Real asset data from GET /assets (40,029 lines)  
- `orders.json` - ✅ Real order data from GET /orders (5,681 lines)
- `products.json` - ✅ Real product data from GET /products (930 lines)
- `warehouses.json` - ✅ Real warehouse data from GET /warehouses (118 lines)
- `offboards.json` - ✅ Real offboard data from GET /offboards (132,145 lines)
- `addresses.json` - ✅ Real address data from GET /employees/{id}/addresses (42 lines)
- `offices.json` - ❌ Endpoint returned 404 Not Found

## Important Notes

⚠️ **PII Data**: These files contain REAL personally identifiable information from your Workwize account:
- Employee names, emails, phone numbers
- Asset assignments and locations  
- Order shipping addresses
- Offboard contact details

🔒 **Security**: 
- These files are already in `.gitignore` and will NOT be committed to Git
- All PII must be scrubbed before caching in the database
- See `docs/PII_SCRUBBING_GUIDELINES.md` for details

## API Endpoints That Work

✅ Available:
- `GET /employees` - Employee records
- `GET /employees/{employee_id}/addresses` - Employee addresses
- `GET /assets` - Asset inventory
- `GET /orders` - Order history
- `GET /products` - Product catalog
- `GET /warehouses` - Warehouse locations
- `GET /offboards` - Offboarding records

❌ Not Available (404):
- `GET /offices` - May require different account tier

**Note**: Address data is available via the employee-specific endpoint and is also embedded within orders and offboards

## Data Structure Notes

### Employees
- Key field: `id` (numeric)
- Contains: `first_name`, `last_name`, `email`, `department`, `job_title`, `user_id`
- Response format: `{ "value": [...] }`

### Assets  
- Key field: `id` (numeric)
- Contains: `name`, `category`, location info, assignment details
- Response format: `{ "data": [...] }`
- Deeply nested structure with product, category, and location details

### Orders
- Key field: `id` (numeric), `number` (string)
- Contains: `actor`, `receiver`, `shipping_info`, `currency`
- Response format: `{ "data": [...] }`

### Products
- Key field: `id` (numeric)
- Contains: `name`, `category`, `description`, `ean`, `article_code`
- Response format: `{ "data": [...] }`

### Warehouses
- Key field: `id` (numeric)
- Contains: `name`, `warehouse_code`, `warehouse_provider`
- Response format: `{ "value": [...] }`

### Offboards
- Key field: `id` (string)
- Contains: `employee_id`, `employee_name`, `email`, `status`, `assets`
- Response format: `{ "data": [...] }`
- Includes nested asset and address data

### Addresses
- Endpoint: `GET /employees/{employee_id}/addresses`
- Response format: `{ "code": 200, "success": true, "data": {...} }`
- Contains: `id`, `address_line_1`, `address_line_2`, `city`, `region`, `postal_code`, `country`
- Includes contact info: `first_name`, `last_name`, `email`, `phone_number`

## Workwize API Documentation

For complete API documentation, visit: https://docs.goworkwize.com/

**Base URL**: `https://prod-back.goworkwize.com/api/public`
