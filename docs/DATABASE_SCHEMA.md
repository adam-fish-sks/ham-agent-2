# Database Schema

## Overview

This document describes the PostgreSQL database schema for the Workwize Management Platform. Data is sourced from the Workwize API (`https://prod-back.goworkwize.com/api/public`) and stored locally with PII scrubbing applied.

**Key Facts**:
- 9 tables (7 from API + 1 lookup table)
- ~1,630 employees, ~3,600 assets, ~140 orders populated
- **94% of employees have addresses** (96 employees lack addresses in Workwize API - this is expected)
- All timestamps include `createdAt` and `updatedAt` fields

---

## ⚠️ Recent Schema Changes (v2.0)

**Migration**: `align_with_workwize_api` - Aligns database schema with Workwize API structure

### Employee (5 new fields)
- `team` (String?) - Team name from API (used in asset location details)
- `foreignId` (String?) - External system reference
- `registrationStatus` (String?) - User registration status (Uninvited, Invited, Registered)
- `isDeactivated` (Boolean) - Active/inactive status (default: false) - **Critical for filtering**
- `userId` (String?) - Workwize user account ID

### Asset (3 renamed, 4 new fields)
**⚠️ BREAKING CHANGES:**
- `serialNumber` → `serialCode` (matches API `serial_code`)
- `purchasePrice` → `invoicePrice` (matches API `invoice_price`)
- `currency` → `invoiceCurrency` (matches API `invoice_currency`)

**New fields:**
- `warehouseStatus` (String?) - available, in_repair, unknown
- `condition` (String?) - new, used
- `tags` (Json?) - Array of tag objects from API
- `externalReference` (String?) - External reference from API

### Order (6 new fields)
- `poNumber` (String?) - Purchase order number
- `totalProducts` (Int?) - Number of products in order
- `receiver` (String?) - Receiver name
- `receiverType` (String?) - employee, office, warehouse
- `expressDelivery` (Boolean) - Express shipping flag (default: false)
- `shippingInfo` (Json?) - Complete shipping address as JSON

### Office (2 new fields)
- `employerId` (String?) - Employer/company ID
- `managerId` (String?) - Manager user ID

### Warehouse (1 new field)
- `warehouseProvider` (String?) - Provider name (e.g., "logistic_plus")

**Migration Instructions**: See [`docs/SCHEMA_MIGRATION_v1_to_v2.md`](SCHEMA_MIGRATION_v1_to_v2.md) for detailed migration steps and impact assessment.

---

## Entity Relationship Diagram

```
                    ┌─────────────────┐
                    │    Address      │
                    │─────────────────│
                    │ id (PK)         │
                    │ city            │
                    │ region          │
                    │ country         │
                    │ postalCode      │
                    │ latitude        │
                    │ longitude       │
                    └─────────────────┘
                            ↑
          ┌─────────────────┼────────────────────────┐
          │                 │                        │
          │ addressId (FK)  │ addressId (FK)        │ addressId (FK)
          │                 │                        │
┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐
│     Office      │  │   Warehouse     │   │   Employee      │
│─────────────────│  │─────────────────│   │─────────────────│
│ id (PK)         │  │ id (PK)         │   │ id (PK)         │
│ name            │  │ name            │   │ firstName *     │
│ code (UQ)       │  │ code (UQ)       │   │ lastName *      │
│ addressId (FK)  │  │ addressId (FK)  │   │ email *         │
│ phone           │  │ capacity        │   │ addressId (FK)  │
│ email           │  │ status          │   │ department      │
│ capacity        │  │ type            │   │ role            │
│ status          │  └─────────────────┘   │ status          │
└─────────────────┘          ↑             │ jobTitle        │
        ↑                    │             │ managerId       │
        │                    │             │ officeId (FK)   │
        │                    │             │ startDate       │
        │ officeId (FK)      │             │ endDate         │
        │                    │             └─────────────────┘
        │                    │                     ↑
        │                    │ warehouseId (FK)    │
        │                    │                     │ employeeId (FK)
        │                    │                     │
        ├────────────────────┼─────────────────────┤
        │                    │                     │
┌─────────────────┐    ┌─────────────────┐  ┌─────────────────┐
│     Asset       │    │     Order       │  │   Offboard      │
│─────────────────│    │─────────────────│  │─────────────────│
│ id (PK)         │    │ id (PK)         │  │ id (PK)         │
│ assetTag (UQ)   │    │ orderNumber (UQ)│  │ employeeId (FK) │
│ name            │    │ status          │  │ offboardDate    │
│ category        │    │ orderDate       │  │ reason          │
│ status          │    │ deliveryDate    │  │ status          │
│ serialNumber    │    │ totalAmount     │  │ returnedAssets  │
│ productId (FK)  │    │ currency        │  │ notes *         │
│ assignedToId(FK)│    │ customerId      │  │ processedBy     │
│ location *      │    │ employeeId (FK) │  └─────────────────┘
│ purchaseDate    │    │ warehouseId(FK) │
│ purchasePrice   │    │ notes           │
│ currency        │    └─────────────────┘
│ warrantyExpires │
│ notes *         │
│ officeId (FK)   │
│ warehouseId(FK) │
└─────────────────┘
        ↑
        │ productId (FK)
        │
┌─────────────────┐
│    Product      │
│─────────────────│
│ id (PK)         │
│ name            │
│ sku (UQ)        │
│ category        │
│ description     │
│ manufacturer    │
│ model           │
│ price           │
│ currency        │
│ status          │
│ stockQuantity   │
└─────────────────┘

┌─────────────────┐
│    Country      │  ← Lookup table (not in API)
│─────────────────│
│ id (PK)         │
│ name            │
│ code (UQ)       │
│ requiresTin     │
│ invoiceCurrency │
│ isOffboardable  │
└─────────────────┘
```

**Legend:**
- `(PK)` = Primary Key
- `(FK)` = Foreign Key
- `(UQ)` = Unique Constraint
- `*` = PII Scrubbed Field (anonymized/redacted before storage)

---

## Table Details

### Employee
**Source**: `GET /employees`, `GET /employees/{id}`
**Population**: 1,630 employees, 1,534 with addresses (94%)

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| id | String | No | Workwize employee ID |
| firstName | String | No | **PII SCRUBBED** - Real data in API |
| lastName | String | No | **PII SCRUBBED** - Real data in API |
| email | String | No | **PII SCRUBBED** - Real data in API |
| addressId | String | Yes | **96 employees (6%) have NULL** - No address in Workwize |
| department | String | Yes | Department name (e.g., "IT", "Sales") |
| role | String | Yes | User role (e.g., "employer-admin", "employee") |
| status | String | Yes | Employment status |
| jobTitle | String | Yes | Job title |
| managerId | String | Yes | Manager employee ID (self-reference) |
| officeId | String | Yes | Office location |
| startDate | DateTime | Yes | Employment start date |
| endDate | DateTime | Yes | Employment end date |
| **team** *NEW* | String | Yes | **Team name** - Used in asset location details |
| **foreignId** *NEW* | String | Yes | **External system reference** |
| **registrationStatus** *NEW* | String | Yes | **Registration status** (Uninvited, Invited, Registered) |
| **isDeactivated** *NEW* | Boolean | No | **Active/inactive status** - Default: false |
| **userId** *NEW* | String | Yes | **Workwize user account ID** |

**Relations**:
- → Address (addressId)
- → Office (officeId)
- ← Asset (many assets assigned)
- ← Order (many orders placed)
- ← Offboard (many offboard records)

### Address
**Source**: `GET /employees/{id}/addresses`
**Population**: 1,534 addresses (94% of employees), 14 warehouse addresses (100%)

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| id | String | No | UUID |
| city | String | Yes | City name |
| region | String | Yes | State/Province |
| country | String | Yes | Country name |
| postalCode | String | Yes | ZIP/Postal code |
| latitude | Float | Yes | GPS coordinate |
| longitude | Float | Yes | GPS coordinate |

**Important**:
- ⚠️ **NO street addresses stored** (PII protection)

**Important**:
- ⚠️ **NO street addresses stored** (PII protection)
- API field `address_line_1`, `address_line_2` are **NOT stored**
- Only general location data (city/region/country) retained
- 404 response expected for 6% of employees (no address in Workwize)

**Relations**:
- ← Employee (many employees)
- ← Office (many offices)
- ← Warehouse (many warehouses)

### Asset
**Source**: `GET /assets`, `GET /assets/{id}`
**Population**: ~3,600 assets with 3 location types

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| id | String | No | Workwize asset ID |
| assetTag | String | No (Unique) | Unique asset identifier |
| name | String | No | Asset name (full product description) |
| category | String | Yes | Category name (e.g., "Laptops") |
| status | String | Yes | Asset status |
| **serialCode** *RENAMED* | String | Yes | **Was: serialNumber** - Serial number from API |
| productId | String | Yes | FK to Product |
| assignedToId | String | Yes | FK to Employee (if assigned to person) |
| location | String | Yes | **PII SCRUBBED** - City/State only |
| purchaseDate | DateTime | Yes | Purchase date |
| **invoicePrice** *RENAMED* | Decimal | Yes | **Was: purchasePrice** - Invoice price from API |
| **invoiceCurrency** *RENAMED* | String | Yes | **Was: currency** - Invoice currency from API |
| warrantyExpires | DateTime | Yes | Warranty expiration |
| notes | String | Yes | **PII SCRUBBED** - Free text |
| officeId | String | Yes | FK to Office (if in office) |
| warehouseId | String | Yes | FK to Warehouse (if in warehouse) |
| **warehouseStatus** *NEW* | String | Yes | **Warehouse status** (available, in_repair, unknown) |
| **condition** *NEW* | String | Yes | **Asset condition** (new, used) |
| **tags** *NEW* | Json | Yes | **Array of tag objects** from API |
| **externalReference** *NEW* | String | Yes | **External reference** from API |

**Location Types from API**:
1. **Employee** (`location_type: "employee"`) - Asset assigned to person
   - Includes: first_name, last_name, address (8 fields), team
2. **Warehouse** (`location_type: "warehouse"`) - Asset in storage
   - Includes: warehouse name only
   - **357 assets** currently in warehouses
3. **Office** (`location_type: "office"`) - Asset at office
   - Includes: office name and full address (8 fields)

**Relations**:
- → Product (productId)
- → Employee (assignedToId) - When assigned to person
- → Office (officeId) - When at office location
- → Warehouse (warehouseId) - When in warehouse

### Warehouse
**Source**: `GET /warehouses?include=countries`
**Population**: 14 warehouses (all with addresses)

### Warehouse
**Source**: `GET /warehouses?include=countries`
**Population**: 14 warehouses (all with country addresses)

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| id | String | No | Workwize warehouse ID |
| name | String | No | Warehouse name (e.g., "Logistics Plus") |
| code | String | Yes (Unique) | Warehouse code (LDW, ER3, VEW, etc.) |
| addressId | String | Yes | FK to Address (contains country info) |
| capacity | Int | Yes | Storage capacity |
| status | String | Yes | Operational status |
| type | String | Yes | Warehouse type |
| **warehouseProvider** *NEW* | String | Yes | **Provider name** (e.g., "logistic_plus") |

**Warehouse Codes & Coverage**:
- **LDW** - United Kingdom, Jersey
- **ER3** - United States  
- **VEW** - 26 European countries (Austria, Belgium, Netherlands, Germany, etc.)
- **LPB** - India
- **LBZ** - Brazil
- **YYZ** - Canada
- **SYD** - Australia
- **LPP** - Philippines
- **MXW** - Mexico

**Address Data**:
- Warehouses have addresses populated via `?include=countries` API parameter
- Address records created with warehouse code as postal code
- Primary country from API countries array is stored in address.country field
- 100% of warehouses have country information available

**Relations**:
- → Address (addressId) - 100% have addresses with country data
- ← Asset (many assets stored)
- ← Order (many orders fulfilled)

### Office
**Source**: `GET /offices`
**Population**: 5 offices (all with addresses)

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| id | String | No | Workwize office ID |
| name | String | No | Office name (e.g., "Amsterdam Office") |
| code | String | Yes (Unique) | Office code |
| addressId | String | Yes | FK to Address |
| phone | String | Yes | Contact phone |
| email | String | Yes | Contact email |
| capacity | Int | Yes | Employee capacity |
| status | String | Yes | Operational status |
| **employerId** *NEW* | String | Yes | **Employer/company ID** from API |
| **managerId** *NEW* | String | Yes | **Manager user ID** from API |

**Office Examples**:
- Amsterdam Office (Netherlands)
- London Office (United Kingdom)
- Washington Office (United States)
- São Paulo Office (Brazil)
- Tokyo Office (Japan)

**Relations**:
- → Address (addressId)
- ← Employee (many employees)
- ← Asset (many assets)

### Order
**Source**: `GET /orders`, `GET /orders/{order_number}/products`
**Population**: ~140 orders

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| id | String | No | Internal order ID |
| orderNumber | String | No (Unique) | Workwize order number |
| status | String | No | Order status |
| orderDate | DateTime | No | Order placement date |
| deliveryDate | DateTime | Yes | Expected/actual delivery |
| totalAmount | Decimal | Yes | Total order value |
| currency | String | Yes | Order currency |
| customerId | String | Yes | Customer identifier |
| employeeId | String | Yes | FK to Employee |
| warehouseId | String | Yes | FK to Warehouse (fulfillment) |
| notes | String | Yes | Order notes |
| **poNumber** *NEW* | String | Yes | **Purchase order number** |
| **totalProducts** *NEW* | Int | Yes | **Number of products** in order |
| **receiver** *NEW* | String | Yes | **Receiver name** |
| **receiverType** *NEW* | String | Yes | **Receiver type** (employee, office, warehouse) |
| **expressDelivery** *NEW* | Boolean | No | **Express shipping** - Default: false |
| **shippingInfo** *NEW* | Json | Yes | **Complete shipping address** as JSON |

**API Filtering**:
- `filter[employee_foreign_id]` - Filter by employee

**Relations**:
- → Employee (employeeId)
- → Warehouse (warehouseId)

### Product
**Source**: `GET /products?include=countries,departments`
**Population**: ~50 products

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| id | String | No | Workwize product ID |
| name | String | No | Product name |
| sku | String | Yes (Unique) | Product SKU |
| category | String | Yes | Product category |
| description | String | Yes | Product description |
| manufacturer | String | Yes | Manufacturer name |
| model | String | Yes | Model number |
| price | Decimal | Yes | Product price |
| currency | String | Yes | Price currency |
| status | String | Yes | Product status |
| stockQuantity | Int | Yes | Available quantity |

**API Filtering**:
- `filter[country_availability]` - Filter by country code
- `include` - Include countries, departments

**Relations**:
- ← Asset (many asset instances)

### Offboard
**Source**: `GET /offboards`
**Population**: ~2,500 offboard records

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| id | String | No | Offboard ID |
| employeeId | String | No | FK to Employee (required) |
| offboardDate | DateTime | No | Offboarding date |
| reason | String | Yes | Offboarding reason |
| status | String | Yes | Status (in_transit_to_warehouse, details_confirmed, etc.) |
| returnedAssets | Boolean | No | Whether assets returned (default: false) |
| notes | String | Yes | **PII SCRUBBED** - Offboard notes |
| processedBy | String | Yes | User who processed offboard |

**Status Values**:
- `in_transit_to_warehouse` - Assets being returned
- `details_confirmed` - Offboard details confirmed
- Others as defined by Workwize

**Relations**:
- → Employee (employeeId) - Required relationship

### Country
**Source**: Manual lookup table (not from API)
**Population**: 387 countries from Workwize

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| id | String | No | Country ID |
| name | String | No | Country name |
| code | String | No (Unique) | ISO country code (e.g., "NL", "US") |
| requiresTin | Boolean | No | Tax ID required (default: false) |
| invoiceCurrency | String | Yes | Default invoice currency |
| isOffboardable | Boolean | No | Can offboard to country (default: true) |

**Countries Requiring TIN**:
- India (IN)
- Brazil (BR)

---

## Key Relationships

### Central Hub: Employee
The Employee table connects most entities:

**Direct Relationships**:
- → Address (94% have addresses, 6% NULL expected)
- → Office (employee location)
- ← Asset (assigned equipment)
- ← Order (purchase orders)
- ← Offboard (termination records)

### Asset Location Hierarchy

**Three Mutually Exclusive Locations**:
1. **Assigned to Employee** (`assignedToId` set)
   - Employee has asset at their location
   - Office/Warehouse IDs typically NULL
   
2. **Stored in Warehouse** (`warehouseId` set)
   - Asset in warehouse storage
   - AssignedTo/Office IDs NULL
   - 357 assets currently warehoused
   
3. **Located at Office** (`officeId` set)
   - Asset at office location
   - AssignedTo/Warehouse IDs NULL

### Address Sharing

**One Address, Many Locations**:
- Multiple offices can share one address
- Multiple warehouses can share one address
- Multiple employees can share one address

---

## Data Quality & Known Issues

### Employee Addresses
- ✅ **1,534 employees (94%)** have addresses
- ⚠️ **96 employees (6%)** have NULL addressId
- **Root Cause**: API returns 404 for these employees
- **Status**: Expected - Workwize data completeness issue
- **Impact**: 83 of these 96 have laptops assigned

### Warehouse Coverage
- ✅ **14/14 warehouses (100%)** have addresses
- ✅ All warehouse codes mapped to countries
- ✅ 357 assets tracked in warehouses

### API Response Inconsistencies
- `GET /employees` → Array (no wrapper)
- `GET /employees/{id}` → Direct object (unwrapped)
- `GET /employees/{id}/addresses` → Wrapped in `{code, success, data}`
- Most other endpoints → Wrapped with pagination

---

---

## PII Scrubbing Strategy

⚠️ **CRITICAL**: All PII must be scrubbed before storage per `docs/PII_SCRUBBING_GUIDELINES.md`

### Fields Currently Scrubbed

**Employee Table** (NOT IMPLEMENTED YET):
- `firstName` → Should be redacted (e.g., "John" → "J***")
- `lastName` → Should be redacted (e.g., "Doe" → "D***")
- `email` → Should be anonymized (e.g., "john.doe@company.com" → "j***@company.com")
- **Current Status**: ⚠️ Real data from API stored directly

**Asset Table** (NOT IMPLEMENTED YET):
- `location` → Should be City/State only (no street addresses)
- `notes` → Should have emails, phones, SSNs redacted
- **Current Status**: ⚠️ Real data from API stored directly

**Address Table** (IMPLEMENTED):
- ✅ `address_line_1` → **NOT STORED** (dropped from schema)
- ✅ `address_line_2` → **NOT STORED** (dropped from schema)
- ✅ Only city, region, country, postalCode retained

**Offboard Table** (NOT IMPLEMENTED YET):
- `notes` → Should have PII redacted
- **Current Status**: ⚠️ Real data from API stored directly

**Order Table** (NOT IMPLEMENTED YET):
- `notes` → Should have PII redacted
- **Current Status**: ⚠️ Real data from API stored directly

### Implementation Status

| Table | PII Fields | Scrubbing Status |
|-------|-----------|------------------|
| Address | street addresses | ✅ IMPLEMENTED (not in schema) |
| Employee | name, email | ⚠️ TODO |
| Asset | location, notes | ⚠️ TODO |
| Offboard | notes | ⚠️ TODO |
| Order | notes | ⚠️ TODO |

---

## Database Statistics (Actual Data)

Based on populated database:
- **Employees**: 1,630 records (1,534 with addresses = 94%)
- **Addresses**: 1,548 records (1,534 employee + 14 warehouse)
- **Assets**: ~3,600 records (357 in warehouses)
- **Orders**: ~140 records
- **Products**: ~50 records  
- **Warehouses**: 14 records (100% with addresses)
- **Offices**: 5 records (100% with addresses)
- **Offboards**: ~2,500 records
- **Countries**: 387 records (lookup table)

### Performance Metrics

**Population Times** (with 10 parallel workers):
- Employees: ~2-3 minutes for 1,630 records
- Assets: ~5 minutes for 3,600 records
- Addresses: ~1 minute for 1,534 employee addresses
- **Total**: ~10-15 minutes for full database population

**Without parallelization**: 10-11 minutes for employees alone

---

## Indexes (Recommended)

For optimal query performance:

```sql
-- Employee lookups
CREATE INDEX idx_employees_office ON employees(officeId);
CREATE INDEX idx_employees_address ON employees(addressId);
CREATE INDEX idx_employees_status ON employees(status);
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_employees_department ON employees(department);

-- Asset lookups  
CREATE INDEX idx_assets_assigned ON assets(assignedToId);
CREATE INDEX idx_assets_product ON assets(productId);
CREATE INDEX idx_assets_office ON assets(officeId);
CREATE INDEX idx_assets_warehouse ON assets(warehouseId);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_category ON assets(category);
CREATE INDEX idx_assets_serial ON assets(serialNumber);

-- Order lookups
CREATE INDEX idx_orders_employee ON orders(employeeId);
CREATE INDEX idx_orders_warehouse ON orders(warehouseId);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_date ON orders(orderDate);
CREATE INDEX idx_orders_number ON orders(orderNumber); -- Unique, but still useful

-- Offboard lookups
CREATE INDEX idx_offboards_employee ON offboards(employeeId);
CREATE INDEX idx_offboards_date ON offboards(offboardDate);
CREATE INDEX idx_offboards_status ON offboards(status);
CREATE INDEX idx_offboards_returned ON offboards(returnedAssets);

-- Address lookups
CREATE INDEX idx_addresses_city ON addresses(city);
CREATE INDEX idx_addresses_country ON addresses(country);

-- Warehouse lookups
CREATE INDEX idx_warehouses_code ON warehouses(code); -- Unique, but still useful

-- Office lookups
CREATE INDEX idx_offices_code ON offices(code); -- Unique, but still useful
```

---

## Common Query Patterns

### Find all assets for an employee
```sql
SELECT a.* 
FROM assets a
WHERE a.assignedToId = 'employee_id';
```

### Find employees without addresses (expected: 96 records)
```sql
SELECT e.id, e.firstName, e.lastName, e.email
FROM employees e
WHERE e.addressId IS NULL;
```

### Find employees with laptops but no address
```sql
SELECT e.id, e.firstName, e.lastName, COUNT(a.id) as laptop_count
FROM employees e
JOIN assets a ON e.id = a.assignedToId
WHERE e.addressId IS NULL
  AND a.category = 'Laptops'
GROUP BY e.id, e.firstName, e.lastName;
```

### Find all assets in a warehouse
```sql
SELECT a.*, w.name as warehouse_name, w.code as warehouse_code
FROM assets a
JOIN warehouses w ON a.warehouseId = w.id
WHERE a.warehouseId IS NOT NULL;
```

### Find all employees in an office with their address
```sql
SELECT e.*, o.name as office_name, addr.city, addr.country
FROM employees e
LEFT JOIN offices o ON e.officeId = o.id
LEFT JOIN addresses addr ON o.addressId = addr.id
WHERE e.officeId IS NOT NULL;
```

### Find offboarded employees who haven't returned assets
```sql
SELECT e.*, o.offboardDate, o.status
FROM employees e
JOIN offboards o ON e.id = o.employeeId
WHERE o.returnedAssets = false
ORDER BY o.offboardDate DESC;
```

### Find all assets in a specific country (via employee location)
```sql
SELECT a.*, e.firstName, e.lastName, addr.country, addr.city
FROM assets a
JOIN employees e ON a.assignedToId = e.id
JOIN addresses addr ON e.addressId = addr.id
WHERE addr.country = 'United States';
```

### Find all assets in a specific country (via warehouse location)
```sql
SELECT a.*, w.name as warehouse_name, addr.country
FROM assets a
JOIN warehouses w ON a.warehouseId = w.id
JOIN addresses addr ON w.addressId = addr.id
WHERE addr.country = 'Netherlands';
```

### Find all assets in a specific country (via office location)
```sql
SELECT a.*, o.name as office_name, addr.country, addr.city
FROM assets a
JOIN offices o ON a.officeId = o.id  
JOIN addresses addr ON o.addressId = addr.id
WHERE addr.country = 'United Kingdom';
```

### Asset count by location type
```sql
SELECT 
  COUNT(CASE WHEN assignedToId IS NOT NULL THEN 1 END) as assigned_to_employee,
  COUNT(CASE WHEN warehouseId IS NOT NULL THEN 1 END) as in_warehouse,
  COUNT(CASE WHEN officeId IS NOT NULL THEN 1 END) as at_office,
  COUNT(*) as total
FROM assets;
```

### Orders pending delivery
```sql
SELECT *
FROM orders
WHERE status = 'pending' 
  AND (deliveryDate IS NULL OR deliveryDate > NOW())
ORDER BY orderDate DESC;
```

---

## API Endpoint Mappings

| Table | Primary Endpoint | Additional Endpoints |
|-------|-----------------|---------------------|
| Employee | `GET /employees` | `GET /employees/{id}` |
| Address | `GET /employees/{id}/addresses` | (embedded in orders, offboards) |
| Asset | `GET /assets` | `GET /assets/{id}` |
| Order | `GET /orders` | `GET /orders/{order_number}/products` |
| Product | `GET /products` | - |
| Warehouse | `GET /warehouses` | - |
| Office | `GET /offices` | - |
| Offboard | `GET /offboards` | - |
| Country | (Manual lookup) | - |

**Authentication**: All endpoints require `Authorization: Bearer {token}`  
**Base URL**: `https://prod-back.goworkwize.com/api/public`

See `docs/WORKWIZE_APIS.md` for complete endpoint documentation with examples.

---

---

## Known Constraints & Limitations

### Unique Constraints
- `Order.orderNumber` - Each order has unique number
- `Product.sku` - Each product has unique SKU (nullable)
- `Asset.assetTag` - Each asset has unique identifier
- `Office.code` - Each office has unique code (nullable)
- `Warehouse.code` - Each warehouse has unique code (nullable)
- `Country.code` - Each country has unique ISO code

### Required Relationships
- `Offboard.employeeId` - Must reference valid employee

### Nullable Foreign Keys (Expected)
- `Employee.addressId` - **96 employees (6%) have NULL** - No address in Workwize
- `Employee.officeId` - Employee may not have assigned office
- `Employee.managerId` - Top-level employees have no manager
- `Order.employeeId` - Some orders not associated with employee
- `Order.warehouseId` - Some orders not associated with warehouse
- `Asset.productId` - Some assets lack product reference
- `Asset.assignedToId` - Unassigned assets (in warehouse/office)
- `Asset.officeId` - Asset not at office
- `Asset.warehouseId` - Asset not in warehouse
- `Office.addressId` - Office may lack address (unlikely)
- `Warehouse.addressId` - Warehouse may lack address (unlikely, 100% populated)

---

## Data Flow Examples

### Asset Lifecycle
1. **Product Created** → Catalog entry (e.g., "MacBook Air M3")
2. **Asset Created** → Physical unit received (serial: YE8MJNJOAQ)
3. **Asset Stored** → Warehouse (warehouseId: 7, LBZ Brazil)
4. **Order Placed** → Employee requests asset
5. **Asset Shipped** → Warehouse to employee
6. **Asset Assigned** → Employee receives (assignedToId set, warehouseId cleared)
7. **Asset In Use** → Employee location (via employee.addressId)
8. **Employee Offboards** → Offboard record created
9. **Asset Returned** → assignedToId cleared, warehouseId set
10. **Asset Available** → Ready for reassignment

### Employee Onboarding
1. **Employee Created** → API sync from Workwize
2. **Address Fetched** → GET /employees/{id}/addresses (may 404)
3. **Address Created** → If available, link via addressId
4. **Office Assigned** → Set officeId if applicable
5. **Assets Assigned** → Laptops, monitors, etc. linked

### Offboarding Process (from API data)
1. **Offboard Initiated** → Record created with employeeId
2. **Status: details_confirmed** → Employee confirms return details
3. **Status: in_transit_to_warehouse** → Assets being returned
4. **Assets Returned** → returnedAssets set to true
5. **Offboard Complete** → Assets reassigned or stored

---

## Future Enhancements

### Recommended Additions
1. **AssetHistory Table** - Track assignment history over time
   - Who had what, when, for how long
   - Audit trail for compliance
   
2. **Department Table** - Normalize department field
   - Separate entity with budget, manager
   - Currently just string in Employee
   
3. **OrderItem Table** - Line items for orders
   - Many-to-many Order ↔ Product
   - Quantities, unit prices
   
4. **AuditLog Table** - Track all modifications
   - User, timestamp, table, action
   - Critical for security compliance
   
5. **Manager Hierarchy** - Enforce managerId as FK
   - Self-referencing Employee.managerId
   - Currently just string reference

6. **AssetMaintenance Table** - Maintenance records
   - Repairs, warranty claims
   - Scheduled maintenance

7. **EmployeeTeam Table** - Team structure
   - Currently embedded in asset location_detail
   - Should be normalized

### PII Scrubbing Implementation
- **CRITICAL TODO**: Implement scrubbing for Employee, Asset, Offboard, Order notes
- Current status: Only Address fields are protected
- See `docs/PII_SCRUBBING_GUIDELINES.md` for requirements

---

## References

- **API Documentation**: `docs/WORKWIZE_APIS.md`
- **PII Guidelines**: `docs/PII_SCRUBBING_GUIDELINES.md`
- **Security Guidelines**: `docs/SECURITY_GUIDELINES.md`
- **Initial Build Guide**: `docs/INITIAL_BUILD.md`
- **Prisma Schema**: `packages/database/schema.prisma`
- **API Data Samples**: `data-samples/*.json`

---

## Schema Version

**Version**: 1.0  
**Last Updated**: February 26, 2026  
**Database**: PostgreSQL 16  
**ORM**: Prisma 6  
**Population Status**: 
- ✅ Employees: 1,630 (94% with addresses)
- ✅ Assets: 3,600 (with location tracking)
- ✅ Warehouses: 14 (100% with addresses)
- ✅ Offices: 5 (100% with addresses)
- ✅ Orders: 140
- ✅ Products: 50
- ✅ Offboards: 2,500
- ✅ Countries: 387
