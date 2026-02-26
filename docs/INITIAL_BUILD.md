# Workwize Management Platform - Initial Build Guide

## Project Overview

Create a Workwize management platform. Data is to be pulled from the Workwize APIs and inserted into a PostgreSQL database in Podman on the local machine.

## Core Requirements

### Database Tables
- Orders
- Products
- Employees
- Assets
- Offices
- Warehouses
- Addresses
- Offboards

### Technology Stack
- **Frontend**: Next.js with Tailwind CSS
- **Backend**: Express.js with Prisma ORM
- **Database**: PostgreSQL 16 in Podman
- **Architecture**: Turborepo monorepo
- **Scripting**: Python for data population

### Key Features
1. Frontend table view for Assets with navigation
2. AI assistant with full data access
3. API data population scripts
4. PII scrubbing compliance

---

## Critical Setup Instructions

### 1. API Configuration

**Base URL**:
```
https://prod-back.goworkwize.com/api/public
```

**Authentication** (⚠️ IMPORTANT):
```bash
# ✅ CORRECT - Use Bearer token
Authorization: Bearer {your_token}

# ❌ WRONG - Do not use X-Api-Key
X-Api-Key: {your_token}
```

**Known API Response Inconsistencies**:
- `GET /employees` → Returns array (no pagination wrapper)
- `GET /employees/{id}` → Returns **direct object** (not wrapped)
- `GET /employees/{id}/addresses` → Returns **wrapped** in `{code, success, data, ...}`
- `GET /assets` → Returns paginated with `{data, links, meta}`
- `GET /orders` → Returns paginated with `{data, links, meta}`

📝 Document all endpoints in `docs/WORKWIZE_APIS.md` with real examples

### 2. Data Samples Strategy

Create `data-samples/` folder containing **real API responses**:
- ✅ Fetch using actual API calls - DO NOT guess at responses
- ✅ Keep as `.json` files (not markdown) for programmatic use
- ✅ Include a `README.md` explaining each file and PII warnings
- ✅ Add to `.gitignore` to prevent committing PII

**Essential files**:
```
data-samples/
  employees.json       # GET /employees
  assets.json          # GET /assets  
  orders.json          # GET /orders
  products.json        # GET /products
  warehouses.json      # GET /warehouses
  offboards.json       # GET /offboards
  addresses.json       # GET /employees/{id}/addresses
  offices.json         # GET /offices (may 404)
  README.md            # Data catalog with warnings
```

### 3. Database Schema Design

**Address Fields** (⚠️ Match Workwize exactly):
```prisma
model Address {
  id        String   @id @default(uuid())
  city      String?  // NOT "line1"
  region    String?  // NOT "state"  
  country   String?
  postalCode String? // NOT "postcode"
  
  // ALWAYS include timestamps
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

**Employee-Address Relationship**:
```prisma
model Employee {
  id        String   @id
  addressId String?  // Nullable - 96 employees may lack addresses
  address   Address? @relation(fields: [addressId], references: [id])
}
```

**Key Lessons**:
- ⚠️ ~6% of employees have no address in Workwize API (returns 404)
- Use nullable foreign keys
- Match Workwize field names exactly (city/region/postalCode)
- Always include createdAt/updatedAt with defaults

### 4. Population Scripts Best Practices

**Performance** (`db-build-scripts/`):
```python
from concurrent.futures import ThreadPoolExecutor

# ✅ Use parallel processing for API calls
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_data, id) for id in ids]
    
# Result: 4-5x speedup (2-3 min vs 10-11 min)
```

**Error Handling**:
```python
# ✅ Handle missing data gracefully
try:
    address = fetch_employee_address(employee_id)
except requests.HTTPError as e:
    if e.response.status_code == 404:
        print(f"No address for employee {employee_id}")
        continue  # Expected for ~6% of employees
    raise
```

**SQL Timestamps**:
```python
# ✅ Always set timestamps explicitly
INSERT INTO addresses (city, region, "postalCode", "createdAt", "updatedAt")
VALUES (%s, %s, %s, NOW(), NOW())

# ❌ Don't omit - causes NOT NULL violations
```

### 5. Git Workflow Configuration

**`.gitignore` Setup**:
```gitignore
# PII Protection
employees_no_address.xlsx
~$*.xlsx

# Build artifacts
.turbo/
packages/frontend/.next/

# Environment
.env

# BUT KEEP: (track for team reference)
data-samples/          # Team needs API structure examples
db-build-scripts/      # Reproducible setup scripts
check-scripts/         # Diagnostic tools
```

**Rationale**: 
- Excel reports with real employee data → Ignore
- Sample JSON for development → Track (PII already in docs as "sanitize before prod")
- Scripts for rebuilding environment → Track

### 6. Development Server Management

**Create `restart_dev.py`**:
```python
# Restart both frontend and backend servers
# Handle port conflicts, stale processes
# Include health checks before reporting "ready"
```

**Known Issue**: Simple restart commands may not work - server may stay down
- Use process management (check for running ports)
- Kill stale Node/Python processes
- Verify DATABASE_URL environment variable

### 7. Data Quality Expectations

**Known API Data Issues**:
- 96/1,630 employees (~6%) have no addresses in Workwize
- 83 of those 96 have laptops assigned
- This is a **Workwize data completeness issue**, not system bug

**Response Strategy**:
1. Document expected data gaps
2. Create Excel reports for manual follow-up
3. Don't block on incomplete data - use nullable fields
4. Create diagnostic scripts in `check-scripts/` folder

### 8. Documentation Requirements

**Essential Documentation** (`docs/`):
```
WORKWIZE_APIS.md           # Complete endpoint reference with examples
PII_SCRUBBING_GUIDELINES.md # Data handling rules
SECURITY_GUIDELINES.md      # Best practices
INITIAL_BUILD.md           # This file
```

**API Documentation Must Include**:
- cURL examples with Bearer token
- Full request/response examples (not summarized)
- Query parameters for each endpoint
- Pagination details (per_page defaults)
- Response wrapper format variations
- Known inconsistencies

### 9. Folder Organization

```
root/
  data-samples/           # Real API JSON responses
  db-build-scripts/       # populate_*.py scripts  
  check-scripts/          # Diagnostic scripts (separate from build)
  docs/                   # All documentation
  packages/
    backend/              # Express.js API
    frontend/             # Next.js UI
    database/             # Prisma schema
```

**Why separate check-scripts**:
- Build scripts = production setup
- Check scripts = debugging/diagnostics
- Clearer separation of concerns

### 10. Azure OpenAI Integration

**Use Lazy Loading**:
```typescript
// ✅ Prevents startup crashes when credentials missing
const getAzureOpenAI = async () => {
  const { AzureOpenAI } = await import('@azure/openai');
  return new AzureOpenAI({ /* config */ });
};
```

**Don't**:
```typescript
// ❌ Crashes server if AZURE_OPENAI_KEY missing
import { AzureOpenAI } from '@azure/openai';
const client = new AzureOpenAI({ /* config */ });
```

---

## Quick Start Checklist

- [ ] Verify API authentication with Bearer token (not X-Api-Key)
- [ ] Confirm base URL: `https://prod-back.goworkwize.com/api/public`
- [ ] Fetch real API samples to `data-samples/` (don't guess)
- [ ] Match Address schema fields to Workwize (city/region/postalCode)
- [ ] Use nullable foreign keys for employee.addressId
- [ ] Include createdAt/updatedAt with defaults on all models
- [ ] Implement parallel processing in population scripts (10 workers)
- [ ] Set up .gitignore for PII (xlsx files) but track data-samples/
- [ ] Create comprehensive API documentation with real examples
- [ ] Document known data gaps (6% employees lack addresses)
- [ ] Separate check-scripts from db-build-scripts folders
- [ ] Lazy-load Azure OpenAI to prevent startup crashes
- [ ] Build robust restart_dev.py with health checks

---

## Common Pitfalls to Avoid

1. **❌ Using X-Api-Key header** → Use `Authorization: Bearer {token}`
2. **❌ Wrong base URL** → Use prod-back.goworkwize.com, not skillsoft
3. **❌ Schema name mismatches** → Use exact Workwize field names
4. **❌ Missing timestamps** → Always include createdAt/updatedAt
5. **❌ Expecting all employees to have addresses** → 6% won't
6. **❌ Sequential API calls** → Use ThreadPoolExecutor for parallelism
7. **❌ Treating all API responses as wrapped** → Check each endpoint's format
8. **❌ Gitignoring all sample data** → Keep data-samples for team reference
9. **❌ Not documenting API with real examples** → AI needs accurate references
10. **❌ Eager-loading Azure OpenAI** → Lazy load to allow graceful degradation

---

## Success Metrics

**Data Population**:
- ✅ 1,500+ employees populated in < 3 minutes
- ✅ 94%+ employees with addresses (6% gap is expected)
- ✅ All assets with location details (employee/warehouse/office)
- ✅ 14/14 warehouses with country mappings

**Documentation**:
- ✅ Complete API docs with cURL examples
- ✅ Response format variations documented
- ✅ Known data gaps documented

**Developer Experience**:
- ✅ Single command to populate database
- ✅ Diagnostic scripts for troubleshooting
- ✅ Clear separation of build vs check scripts
- ✅ Development servers restart reliably