# Schema v2.0 - Quick Reference

## What Changed?

### Employee (5 new fields)

- `team` - Team name from API
- `foreignId` - External system reference
- `registrationStatus` - Uninvited, Invited, Registered
- `isDeactivated` - Active/inactive status (default: false)
- `userId` - Workwize user account ID

### Asset (3 renamed + 4 new)

**⚠️ BREAKING CHANGES:**

- `serialNumber` → `serialCode`
- `purchasePrice` → `invoicePrice`
- `currency` → `invoiceCurrency`

**New:**

- `warehouseStatus` - available, in_repair, unknown
- `condition` - new, used
- `tags` - JSON array of tag objects
- `externalReference` - External reference ID

### Order (6 new fields)

- `poNumber` - Purchase order number
- `totalProducts` - Product count
- `receiver` - Receiver name
- `receiverType` - employee, office, warehouse
- `expressDelivery` - Express flag (default: false)
- `shippingInfo` - JSON shipping address

### Office (2 new fields)

- `employerId` - Employer/company ID
- `managerId` - Manager user ID

### Warehouse (1 new field)

- `warehouseProvider` - Provider name (e.g., "logistic_plus")

---

## Quick Migration (When DB is running)

```bash
# 1. Generate migration
cd packages/database
npx prisma migrate dev --name align_with_workwize_api

# 2. Update population scripts (see MIGRATION_CHECKLIST.md)

# 3. Search & replace in code:
#    serialNumber → serialCode
#    purchasePrice → invoicePrice
#    currency → invoiceCurrency (Asset context only!)

# 4. Re-run population
cd ../../db-build-scripts
python populate_all.py
```

---

## Documents Created

1. **[SCHEMA_MIGRATION_v1_to_v2.md](SCHEMA_MIGRATION_v1_to_v2.md)** - Detailed migration strategy
2. **[MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md)** - Step-by-step execution guide
3. **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Updated with all new fields

---

## Why These Changes?

1. **API Alignment**: Schema now matches Workwize API exactly
2. **No Data Loss**: All API fields captured
3. **Better Naming**: Field names match API conventions
4. **Future Features**: Enables tagging, user filtering, shipping tracking

---

## Risk Level: LOW-MEDIUM

- ✅ All new fields are nullable
- ✅ No data loss from additions
- ⚠️ 3 field renames require code updates
- ⚠️ ~5 files need updating

---

**Status**: Schema updated, migration ready to execute
**Next**: See [MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md) Phase 2
