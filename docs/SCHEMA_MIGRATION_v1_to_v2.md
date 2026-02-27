# Schema Migration: v1.0 → v2.0

**Date**: February 26, 2026  
**Purpose**: Align database schema with Workwize API structure

---

## Overview

This migration adds missing API fields and renames fields to match Workwize API naming conventions for better alignment and future maintenance.

---

## Changes by Table

### Employee Table

**Added Fields:**

- `team` (String?) - Team name from API
- `foreignId` (String?) - External system reference
- `registrationStatus` (String?) - User registration status (Uninvited, Invited, Registered)
- `isDeactivated` (Boolean) - Active/inactive status (default: false)
- `userId` (String?) - Workwize user account ID

**Rationale**:

- `team` is used throughout asset location details
- `isDeactivated` is critical for filtering active employees
- `registrationStatus` needed for onboarding tracking
- `userId` and `foreignId` enable better system integration

### Asset Table

**Renamed Fields:**

- `serialNumber` → `serialCode` (matches API: `serial_code`)
- `purchasePrice` → `invoicePrice` (matches API: `invoice_price`)
- `currency` → `invoiceCurrency` (matches API: `invoice_currency`)

**Added Fields:**

- `warehouseStatus` (String?) - available, in_repair, unknown
- `condition` (String?) - new, used
- `tags` (Json?) - Array of tag objects from API
- `externalReference` (String?) - External reference from API

**Rationale**:

- Field names now match API exactly for easier maintenance
- `warehouseStatus` and `condition` are in every API response
- `tags` enables asset tagging/categorization feature
- `externalReference` supports external system integration

### Order Table

**Added Fields:**

- `poNumber` (String?) - Purchase order number
- `totalProducts` (Int?) - Number of products in order
- `receiver` (String?) - Receiver name
- `receiverType` (String?) - employee, office, warehouse
- `expressDelivery` (Boolean) - Express shipping flag (default: false)
- `shippingInfo` (Json?) - Complete shipping address as JSON

**Rationale**:

- API provides rich order metadata not previously captured
- `shippingInfo` preserves complete address for order tracking
- `receiver` and `receiverType` clarify order destination

### Office Table

**Added Fields:**

- `employerId` (String?) - Employer/company ID
- `managerId` (String?) - Manager user ID

**Rationale**:

- Links office to employer organization
- Tracks office manager for reporting

### Warehouse Table

**Added Fields:**

- `warehouseProvider` (String?) - Provider name (e.g., "logistic_plus")

**Rationale**:

- All warehouses have a provider in API
- Useful for logistics tracking

---

## Migration Strategy

### Phase 1: Add New Fields (Non-Breaking)

```bash
# Generate migration for new fields
npx prisma migrate dev --name add_api_fields
```

### Phase 2: Data Migration (Column Renames)

**⚠️ BREAKING CHANGES** - These require data migration:

```sql
-- Asset table renames
ALTER TABLE assets RENAME COLUMN "serialNumber" TO "serialCode";
ALTER TABLE assets RENAME COLUMN "purchasePrice" TO "invoicePrice";
ALTER TABLE assets RENAME COLUMN "currency" TO "invoiceCurrency";
```

**Affected Components:**

1. `populate_assets.py` - Update field names
2. Frontend Assets page - Update column references
3. Any queries using old field names

### Phase 3: Populate New Fields

**Employee Fields:**

```python
# populate_employees.py updates needed
employee_data = {
    'team': api_response.get('team'),
    'foreignId': api_response.get('foreign_id'),
    'registrationStatus': api_response.get('registrationStatus'),
    'isDeactivated': api_response.get('isDeactivated', False),
    'userId': api_response.get('user_id')
}
```

**Asset Fields:**

```python
# populate_assets.py updates needed
asset_data = {
    'warehouseStatus': api_response.get('warehouse_status'),
    'condition': api_response.get('condition'),
    'tags': json.dumps(api_response.get('tags', [])),
    'externalReference': api_response.get('external_reference')
}
```

---

## Rollback Plan

If issues arise:

```sql
-- Rollback asset renames
ALTER TABLE assets RENAME COLUMN "serialCode" TO "serialNumber";
ALTER TABLE assets RENAME COLUMN "invoicePrice" TO "purchasePrice";
ALTER TABLE assets RENAME COLUMN "invoiceCurrency" TO "currency";

-- Drop new fields (if needed)
ALTER TABLE employees DROP COLUMN team;
ALTER TABLE employees DROP COLUMN "foreignId";
-- ... (continue for other new fields)
```

---

## Testing Checklist

- [ ] Generate migration successfully
- [ ] Apply migration to dev database
- [ ] Update populate_employees.py with new fields
- [ ] Update populate_assets.py with renamed + new fields
- [ ] Run population scripts to verify data loads
- [ ] Test frontend Assets page with renamed fields
- [ ] Verify queries still work with new field names
- [ ] Check that isDeactivated defaults to false
- [ ] Test JSON fields (tags, shippingInfo) serialize correctly
- [ ] Run full database population (10-15 min)
- [ ] Verify no data loss from renames

---

## Impact Assessment

**Low Risk:**

- All new fields are nullable (except isDeactivated with default)
- No data loss from additions

**Medium Risk:**

- Field renames require code updates
- 3 files need immediate updates (populate scripts, frontend)

**High Risk:**

- None - all changes are additive or renames with clear migration path

---

## Post-Migration Tasks

1. Update `docs/DATABASE_SCHEMA.md` with new fields
2. Update `docs/WORKWIZE_APIS.md` field mappings
3. Document field name changes in git commit
4. Update Excel export script for new employee fields
5. Consider adding indexes for new commonly-queried fields:
   ```sql
   CREATE INDEX idx_employees_deactivated ON employees(isDeactivated);
   CREATE INDEX idx_employees_team ON employees(team);
   CREATE INDEX idx_assets_warehouse_status ON assets(warehouseStatus);
   ```

---

## Schema Version

**Before**: v1.0  
**After**: v2.0  
**Migration**: `20260226_add_api_fields`
