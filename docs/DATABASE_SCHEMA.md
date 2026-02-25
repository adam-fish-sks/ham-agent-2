# Database Schema

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
        │
        │ addressId (FK)
        │
    ┌───┴────────────────────────────────┐
    │                                    │
┌─────────────────┐              ┌─────────────────┐
│     Office      │              │   Warehouse     │
│─────────────────│              │─────────────────│
│ id (PK)         │              │ id (PK)         │
│ name            │              │ name            │
│ code (UQ)       │              │ code (UQ)       │
│ addressId (FK)  │              │ addressId (FK)  │
│ phone           │              │ capacity        │
│ email           │              │ status          │
│ capacity        │              │ type            │
│ status          │              └─────────────────┘
└─────────────────┘                      ↑
        ↑                                │
        │                                │
        │ officeId (FK)                  │ warehouseId (FK)
        │                                │
        ├────────────────────────────────┼────────────────────┐
        │                                │                    │
┌─────────────────┐              ┌─────────────────┐  ┌─────────────────┐
│    Employee     │              │     Asset       │  │     Order       │
│─────────────────│              │─────────────────│  │─────────────────│
│ id (PK)         │──────────────│ id (PK)         │  │ id (PK)         │
│ firstName *     │  assignedTo  │ assetTag (UQ)   │  │ orderNumber (UQ)│
│ lastName *      │              │ name            │  │ status          │
│ email *         │              │ category        │  │ orderDate       │
│ department      │              │ status          │  │ deliveryDate    │
│ role            │              │ serialNumber    │  │ totalAmount     │
│ status          │              │ productId (FK)  │  │ currency        │
│ jobTitle        │              │ assignedToId(FK)│  │ customerId      │
│ managerId       │              │ location *      │  │ employeeId (FK) │
│ officeId (FK)   │              │ purchaseDate    │  │ warehouseId(FK) │
│ startDate       │              │ purchasePrice   │  │ notes           │
│ endDate         │              │ currency        │  └─────────────────┘
└─────────────────┘              │ warrantyExpires │          ↑
        ↑                        │ notes *         │          │
        │                        │ officeId (FK)   │          │
        │ employeeId (FK)        │ warehouseId(FK) │          │
        │                        └─────────────────┘          │
        │                                ↑                    │
        │                                │                    │
        │                                │ productId (FK)     │
        │                                │                    │
        │                        ┌─────────────────┐          │
        │                        │    Product      │          │
        │                        │─────────────────│          │
        │                        │ id (PK)         │          │
        │                        │ name            │──────────┘
        │                        │ sku (UQ)        │
        │                        │ category        │
        │                        │ description     │
        │                        │ manufacturer    │
        │                        │ model           │
        │                        │ price           │
        │                        │ currency        │
        │                        │ status          │
        │                        │ stockQuantity   │
        │                        └─────────────────┘
        │
        │ employeeId (FK)
        │
┌─────────────────┐
│    Offboard     │
│─────────────────│
│ id (PK)         │
│ employeeId (FK) │
│ offboardDate    │
│ reason          │
│ status          │
│ returnedAssets  │
│ notes           │
│ processedBy     │
└─────────────────┘
```

**Legend:**
- `(PK)` = Primary Key
- `(FK)` = Foreign Key
- `(UQ)` = Unique Constraint
- `*` = PII Scrubbed Field (anonymized/redacted before storage)

---

## Table Relationships

### Central Hub: **Employee**
The Employee table is the central entity connecting most of the system:

**Outgoing Relationships (1:N):**
- → **Asset** (assigned assets via `assignedToId`)
- → **Order** (orders associated with employee via `employeeId`)
- → **Offboard** (offboarding records via `employeeId`)

**Incoming Relationships (N:1):**
- ← **Office** (employee works at office via `officeId`)

---

### Location Hierarchy: **Address → Office/Warehouse**

**Address** (parent)
- → **Office** (1:N via `addressId`)
- → **Warehouse** (1:N via `addressId`)

Each office and warehouse can have one address. Multiple offices/warehouses can share the same address.

---

### Asset Management: **Product → Asset → Employee/Office/Warehouse**

**Product** (catalog item)
- → **Asset** (1:N via `productId`) - Each product can have multiple asset instances

**Asset** (physical item)
- ← **Product** (N:1 via `productId`) - Each asset is one product type
- ← **Employee** (N:1 via `assignedToId`) - Who has it
- ← **Office** (N:1 via `officeId`) - Where it's located (office)
- ← **Warehouse** (N:1 via `warehouseId`) - Where it's stored (warehouse)

---

### Order Processing: **Order → Employee/Warehouse**

**Order**
- ← **Employee** (N:1 via `employeeId`) - Who placed/owns the order
- ← **Warehouse** (N:1 via `warehouseId`) - Which warehouse fulfills it

---

### Employee Lifecycle: **Employee → Offboard**

**Offboard** (termination records)
- ← **Employee** (N:1 via `employeeId`) - Which employee was offboarded

---

## PII Scrubbing Strategy

The following fields are **scrubbed** before being stored in PostgreSQL:

### Employee Table
- `firstName` → Redacted to first letter + asterisks (e.g., "John" → "J***")
- `lastName` → Redacted to first letter + asterisks (e.g., "Doe" → "D***")
- `email` → Anonymized (e.g., "john.doe@company.com" → "j***@company.com")

### Asset Table
- `location` → City/State only (street addresses removed)
- `notes` → Emails, phone numbers, SSNs, credit cards redacted

### Address Table
- `addressLine1` → **NOT STORED** (completely removed)
- `addressLine2` → **NOT STORED** (completely removed)
- Only keeps: city, region, country, postalCode (general location data)

### Offboard Table
- `notes` → Emails, phone numbers, SSNs, credit cards redacted

---

## Key Constraints

### Unique Constraints
- `Order.orderNumber` - Each order has unique number
- `Product.sku` - Each product has unique SKU
- `Asset.assetTag` - Each asset has unique tag
- `Office.code` - Each office has unique code
- `Warehouse.code` - Each warehouse has unique code

### Required Relationships
- `Offboard.employeeId` - Cannot be null (must reference an employee)

### Optional Relationships (nullable FKs)
- `Employee.officeId` - Employee may not have assigned office
- `Order.employeeId` - Order may not have associated employee
- `Order.warehouseId` - Order may not have warehouse
- `Asset.productId` - Asset may not have product reference
- `Asset.assignedToId` - Asset may not be assigned
- `Asset.officeId` - Asset may not be in office
- `Asset.warehouseId` - Asset may not be in warehouse
- `Office.addressId` - Office may not have address
- `Warehouse.addressId` - Warehouse may not have address

---

## Data Flow Example

### Typical Asset Lifecycle
1. **Product Created** → New product added to catalog (e.g., "MacBook Pro 16")
2. **Asset Created** → Physical instance received (assigned `assetTag`, linked to `productId`)
3. **Asset Stored** → Placed in warehouse (set `warehouseId`)
4. **Order Created** → Employee requests asset (creates `Order` with `employeeId`)
5. **Asset Assigned** → Asset allocated to employee (set `assignedToId`, clear `warehouseId`)
6. **Employee Works** → Asset in use at employee's office location
7. **Employee Leaves** → Offboard created (set `Offboard.employeeId`)
8. **Asset Returned** → Asset unassigned (clear `assignedToId`, set `returnedAssets = true` in Offboard)
9. **Asset Stored** → Back to warehouse or reassigned

### Typical Query Patterns

**Find all assets for an employee:**
```sql
SELECT * FROM assets WHERE assignedToId = 'employee_id'
```

**Find all employees in an office:**
```sql
SELECT * FROM employees WHERE officeId = 'office_id'
```

**Find all orders pending delivery:**
```sql
SELECT * FROM orders WHERE status = 'pending' AND deliveryDate > NOW()
```

**Find offboarded employees who haven't returned assets:**
```sql
SELECT e.*, o.* FROM employees e
JOIN offboards o ON e.id = o.employeeId
WHERE o.returnedAssets = false
```

**Find all assets in a specific city:**
```sql
SELECT a.* FROM assets a
JOIN offices o ON a.officeId = o.id
JOIN addresses addr ON o.addressId = addr.id
WHERE addr.city = 'Amsterdam'
```

---

## Database Statistics (from real API data)

Based on the Workwize API samples:
- **Employees**: ~1,000+ records (58KB response)
- **Assets**: ~800+ records (40KB response)
- **Orders**: ~100+ records (5.6KB response)
- **Products**: ~50+ records (930 bytes response)
- **Warehouses**: ~5-10 records (118 bytes response)
- **Offboards**: ~2,500+ records (132KB response)
- **Addresses**: Available per employee (42 bytes response)
- **Offices**: Not available in API

---

## Indexes Recommended

For optimal query performance, consider these indexes:

```sql
-- Employee lookups
CREATE INDEX idx_employees_office ON employees(officeId);
CREATE INDEX idx_employees_status ON employees(status);
CREATE INDEX idx_employees_email ON employees(email);

-- Asset lookups
CREATE INDEX idx_assets_assigned ON assets(assignedToId);
CREATE INDEX idx_assets_product ON assets(productId);
CREATE INDEX idx_assets_office ON assets(officeId);
CREATE INDEX idx_assets_warehouse ON assets(warehouseId);
CREATE INDEX idx_assets_status ON assets(status);

-- Order lookups
CREATE INDEX idx_orders_employee ON orders(employeeId);
CREATE INDEX idx_orders_warehouse ON orders(warehouseId);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_date ON orders(orderDate);

-- Offboard lookups
CREATE INDEX idx_offboards_employee ON offboards(employeeId);
CREATE INDEX idx_offboards_date ON offboards(offboardDate);
CREATE INDEX idx_offboards_status ON offboards(status);
```

---

## Future Enhancements

Potential schema improvements:
1. **Order Items** - Break out line items from orders (many-to-many Order ↔ Product)
2. **Asset History** - Track asset assignment history over time
3. **Department** - Separate department entity instead of string field
4. **Manager Relationship** - Self-referencing Employee.managerId as FK
5. **Address History** - Track office/warehouse address changes
6. **Audit Log** - Track all data modifications with timestamps and user IDs
