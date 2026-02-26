# Migration Checklist: Schema v2.0

**Status**: ⚠️ **PENDING** - Schema updated in Prisma but migration not yet applied

---

## Quick Summary

- **19 new fields** added across 5 tables
- **3 fields renamed** in Asset table (BREAKING)
- **All changes are nullable** (except defaults)
- **Migration name**: `align_with_workwize_api`

---

## Step-by-Step Migration

### ✅ Phase 1: Schema Updates (COMPLETED)
- [x] Update Employee model with 5 new fields
- [x] Update Asset model with renamed + new fields
- [x] Update Order model with 6 new fields
- [x] Update Office model with 2 new fields
- [x] Update Warehouse model with 1 new field
- [x] Document changes in DATABASE_SCHEMA.md
- [x] Create SCHEMA_MIGRATION_v1_to_v2.md

### ⚠️ Phase 2: Database Migration (PENDING)

**Prerequisites**:
1. Ensure `.env` file exists with DATABASE_URL
2. Database is running and accessible
3. Backup existing data (optional but recommended)

**Commands**:
```bash
# Navigate to database package
cd packages/database

# Generate and apply migration
npx prisma migrate dev --name align_with_workwize_api

# Verify migration was created
ls -la prisma/migrations
```

**Expected Output**:
```
✔ Generated Prisma Client
The following migration(s) have been created and applied:

migrations/
  └─ 20260226XXXXXX_align_with_workwize_api/
    └─ migration.sql

✔ Your database is now in sync with your schema.
```

**What This Does**:
- Adds 19 new nullable columns
- Renames 3 Asset columns
- Updates Prisma Client types
- Creates migration history entry

---

### ⚠️ Phase 3: Population Scripts (CRITICAL)

**Files to Update**:

#### 1. `db-build-scripts/populate_assets.py`

**Field Name Changes** (BREAKING):
```python
# OLD → NEW
'serialNumber' → 'serialCode'
'purchasePrice' → 'invoicePrice'
'currency' → 'invoiceCurrency'
```

**Search & Replace**:
```python
# Find all occurrences of:
data['serialNumber'] = ...
data['purchasePrice'] = ...
data['currency'] = ...

# Replace with:
data['serialCode'] = api_response.get('serial_code')
data['invoicePrice'] = api_response.get('invoice_price')
data['invoiceCurrency'] = api_response.get('invoice_currency')
```

**New Fields to Add**:
```python
asset_data = {
    # ... existing fields ...
    'warehouseStatus': api_response.get('warehouse_status'),
    'condition': api_response.get('condition'),
    'tags': json.dumps(api_response.get('tags', [])),  # Store as JSON string
    'externalReference': api_response.get('external_reference')
}
```

#### 2. `db-build-scripts/populate_employees.py`

**New Fields to Add**:
```python
employee_data = {
    # ... existing fields ...
    'team': api_response.get('team'),
    'foreignId': api_response.get('foreign_id'),
    'registrationStatus': api_response.get('registrationStatus'),
    'isDeactivated': api_response.get('isDeactivated', False),  # Default to False
    'userId': api_response.get('user_id')
}
```

#### 3. `db-build-scripts/populate_orders.py`

**New Fields to Add**:
```python
order_data = {
    # ... existing fields ...
    'poNumber': api_response.get('po_number'),
    'totalProducts': api_response.get('total_products'),
    'receiver': api_response.get('receiver'),
    'receiverType': api_response.get('receiver_type'),
    'expressDelivery': api_response.get('express_delivery', False),
    'shippingInfo': json.dumps(api_response.get('shipping_info', {}))  # Store as JSON
}
```

#### 4. `db-build-scripts/populate_warehouses.py`

**New Field to Add**:
```python
warehouse_data = {
    # ... existing fields ...
    'warehouseProvider': api_response.get('warehouse_provider', 'logistic_plus')
}
```

#### 5. `db-build-scripts/populate_offices.py`

**New Fields to Add**:
```python
office_data = {
    # ... existing fields ...
    'employerId': api_response.get('employer_id'),
    'managerId': api_response.get('manager', {}).get('id')  # Extract from nested object
}
```

---

### ⚠️ Phase 4: Frontend Updates (BREAKING)

**Files to Search**:
- `packages/frontend/src/**/*.ts`
- `packages/frontend/src/**/*.tsx`

**Search Terms**:
1. `serialNumber` (in Asset context)
2. `purchasePrice` (in Asset context)
3. `currency` (in Asset context - be careful not to change Order.currency)

**Component Files Likely Affected**:
- Asset list/table components
- Asset detail pages
- Any export/report components

**Example Changes**:
```typescript
// OLD
<TableCell>{asset.serialNumber}</TableCell>
<TableCell>{asset.purchasePrice}</TableCell>
<TableCell>{asset.currency}</TableCell>

// NEW
<TableCell>{asset.serialCode}</TableCell>
<TableCell>{asset.invoicePrice}</TableCell>
<TableCell>{asset.invoiceCurrency}</TableCell>
```

**Search Commands**:
```bash
# Find all references to old field names
cd packages/frontend
grep -r "serialNumber" src/
grep -r "purchasePrice" src/
grep -r "\.currency" src/  # Use \. to match asset.currency specifically
```

---

### ⚠️ Phase 5: Backend Updates (BREAKING)

**Files to Search**:
- `packages/backend/src/**/*.ts`

**Same field renames apply** - Update all queries and API endpoints

**Example Backend Query Update**:
```typescript
// OLD
const assets = await prisma.asset.findMany({
  select: {
    serialNumber: true,
    purchasePrice: true,
    currency: true
  }
});

// NEW
const assets = await prisma.asset.findMany({
  select: {
    serialCode: true,
    invoicePrice: true,
    invoiceCurrency: true
  }
});
```

---

### ⚠️ Phase 6: Testing

**Test Checklist**:
- [ ] Run all population scripts without errors
- [ ] Verify new fields populated in database
- [ ] Frontend Assets page loads correctly
- [ ] No console errors about missing fields
- [ ] Asset detail pages display correctly
- [ ] Country column (uses invoiceCurrency) still works
- [ ] Excel export includes new fields
- [ ] Filtering by isDeactivated works
- [ ] Tags display correctly (if implemented)
- [ ] Order shipping info displays (if implemented)

**SQL Verification Queries**:
```sql
-- Check if new Employee fields populated
SELECT 
  COUNT(*) as total,
  COUNT(team) as with_team,
  COUNT("foreignId") as with_foreign_id,
  COUNT("userId") as with_user_id,
  COUNT(CASE WHEN "isDeactivated" = true THEN 1 END) as deactivated
FROM employees;

-- Check if Asset fields renamed
SELECT 
  COUNT(*) as total,
  COUNT("serialCode") as with_serial_code,
  COUNT("invoicePrice") as with_invoice_price,
  COUNT("invoiceCurrency") as with_currency,
  COUNT(tags) as with_tags
FROM assets;

-- Check if Order fields populated
SELECT 
  COUNT(*) as total,
  COUNT("poNumber") as with_po,
  COUNT("totalProducts") as with_products,
  COUNT("shippingInfo") as with_shipping
FROM orders;
```

---

### ⚠️ Phase 7: Documentation Updates

- [ ] Update DATABASE_SCHEMA.md field counts
- [ ] Update WORKWIZE_APIS.md field mappings
- [ ] Update any ERD diagrams
- [ ] Document new query patterns
- [ ] Update Excel export script docs

---

## Rollback Plan

If something goes wrong:

```bash
# Option 1: Rollback last migration
cd packages/database
npx prisma migrate resolve --rolled-back 20260226XXXXXX_align_with_workwize_api

# Option 2: Manual SQL rollback (if needed)
psql -U ham_agent_2 -d ham_agent_2_db

-- Drop new columns
ALTER TABLE employees DROP COLUMN team;
ALTER TABLE employees DROP COLUMN "foreignId";
ALTER TABLE employees DROP COLUMN "registrationStatus";
ALTER TABLE employees DROP COLUMN "isDeactivated";
ALTER TABLE employees DROP COLUMN "userId";

-- Rename Asset columns back
ALTER TABLE assets RENAME COLUMN "serialCode" TO "serialNumber";
ALTER TABLE assets RENAME COLUMN "invoicePrice" TO "purchasePrice";
ALTER TABLE assets RENAME COLUMN "invoiceCurrency" TO "currency";

-- Drop other new columns
ALTER TABLE assets DROP COLUMN "warehouseStatus";
ALTER TABLE assets DROP COLUMN condition;
ALTER TABLE assets DROP COLUMN tags;
ALTER TABLE assets DROP COLUMN "externalReference";

-- ... (continue for other tables)
```

---

## Migration Timeline Estimate

| Phase | Time Estimate | Blocking? |
|-------|---------------|-----------|
| Phase 2: Database Migration | 2 minutes | Yes |
| Phase 3: Population Scripts | 30-45 minutes | Yes |
| Phase 4: Frontend Updates | 15-30 minutes | Yes |
| Phase 5: Backend Updates | 15-20 minutes | Yes |
| Phase 6: Testing | 30-60 minutes | No |
| Phase 7: Documentation | 15 minutes | No |
| **Total** | **~2-3 hours** | - |

---

## Success Criteria

✅ **Migration Successful When**:
1. Database migration applied without errors
2. All population scripts run successfully
3. Frontend loads without console errors
4. Asset field renames reflected everywhere
5. New fields populated from API
6. Tests pass (if any exist)
7. No references to old field names remain

---

## Post-Migration Enhancements (Optional)

**Consider Adding**:
1. Indexes for commonly filtered fields:
   ```sql
   CREATE INDEX idx_employees_deactivated ON employees("isDeactivated");
   CREATE INDEX idx_employees_team ON employees(team);
   CREATE INDEX idx_assets_warehouse_status ON assets("warehouseStatus");
   ```

2. Frontend components for new features:
   - Asset tagging UI (uses `tags` field)
   - Employee status filter (uses `isDeactivated`)
   - Order shipping tracker (uses `shippingInfo`)

3. New query patterns:
   - Filter active employees only
   - Group assets by warehouse status
   - Track express deliveries

---

## Notes

- **Breaking Changes**: Only Asset field renames are breaking
- **Data Safety**: All new fields nullable - no data loss
- **API Alignment**: Schema now matches API structure exactly
- **Future-Proof**: Capturing all API fields prevents future gaps

---

**Last Updated**: 2026-02-26
**Migration Status**: Ready to execute
**Next Action**: Run Phase 2 (Database Migration)
