# PII Scrubbing Guidelines

## Overview

When caching data from WorkWize API that contains Personally Identifiable Information (PII), **all PII must be scrubbed** before storing in the database cache.

## What is PII?

PII includes but is not limited to:

- Full names (first name, last name)
- Email addresses
- Phone numbers
- Street addresses
- Social Security Numbers
- Credit card numbers
- Any other information that can identify an individual

## Required PII Scrubbing

### Employee Data

When caching employee data, use the `scrubEmployeeForCache()` function:

```typescript
import { scrubEmployeeForCache } from '@ham-agent/shared';
import { prisma } from '@ham-agent/database';

// ❌ WRONG - Stores PII directly
await prisma.employee.upsert({
  where: { id: employee.id },
  create: {
    id: employee.id,
    firstName: employee.firstName, // PII
    lastName: employee.lastName,   // PII
    email: employee.email,         // PII
    department: employee.department,
    role: employee.role,
    status: employee.status,
  },
  update: { ... }
});

// ✅ CORRECT - Scrubs PII before caching
const scrubbedEmployee = scrubEmployeeForCache(employee);
await prisma.employee.upsert({
  where: { id: scrubbedEmployee.id },
  create: scrubbedEmployee,
  update: scrubbedEmployee,
});
```

Scrubbed employee data example:

```typescript
{
  id: "123",
  firstName: "J***",      // Redacted to initial
  lastName: "D***",       // Redacted to initial
  email: "j***@company.com",  // Anonymized
  department: "Engineering",
  role: "Developer",
  status: "active"
}
```

### Asset Data

When caching asset data, use the `scrubAssetForCache()` function:

```typescript
import { scrubAssetForCache } from '@ham-agent/shared';

const scrubbedAsset = scrubAssetForCache(asset);
await prisma.asset.upsert({
  where: { id: scrubbedAsset.id },
  create: scrubbedAsset,
  update: scrubbedAsset,
});
```

Scrubbed asset data:

- **Assigned To**: Only stores employee ID, not name
- **Location**: Only stores city/state, removes street addresses
- **Notes**: Scrubs emails, phone numbers, SSNs, credit cards

## Individual Scrubbing Functions

For custom scrubbing needs:

### Anonymize Email

```typescript
import { anonymizeEmail } from '@ham-agent/shared';

const email = anonymizeEmail('john.doe@company.com');
// Result: "j***@company.com"
```

### Redact Name

```typescript
import { redactName } from '@ham-agent/shared';

const name = redactName('John');
// Result: "J***"
```

### Scrub Address

```typescript
import { scrubAddress } from '@ham-agent/shared';

const location = scrubAddress({
  address_line_1: '123 Main Street',
  city: 'New York',
  region: 'NY',
  postal_code: '10001',
});
// Result: "New York, NY"
```

### Scrub Text

```typescript
import { scrubText } from '@ham-agent/shared';

const notes = scrubText('Contact john.doe@company.com or call 555-123-4567');
// Result: "Contact [EMAIL_REDACTED] or call [PHONE_REDACTED]"
```

## Validation

Before caching, validate that PII has been properly scrubbed:

```typescript
import { validateScrubbed } from '@ham-agent/shared';

const scrubbedData = scrubEmployeeForCache(employee);

if (!validateScrubbed(scrubbedData)) {
  console.error('PII scrubbing failed - data contains potential PII');
  throw new Error('PII validation failed');
}

// Safe to cache
await prisma.employee.create({ data: scrubbedData });
```

## When to Scrub

**ALWAYS scrub PII when:**

1. Storing data in database cache
2. Storing data in Redis cache
3. Logging employee or customer data
4. Exposing data through public APIs
5. Generating reports or exports

**DO NOT scrub when:**

1. Making direct API calls to WorkWize (keep original data for API requests)
2. Displaying data in authenticated, authorized UI (show original from WorkWize API)
3. Processing data transiently in memory (scrub only before persistence)

## Implementation Checklist

When implementing caching:

- [ ] Import scrubbing utilities from `@ham-agent/shared`
- [ ] Call appropriate scrubbing function before database write
- [ ] Validate scrubbed data with `validateScrubbed()`
- [ ] Log scrubbing activity for audit purposes
- [ ] Never log the original PII data
- [ ] Document why data is being cached and PII handling

## Example: Complete Cache Implementation

```typescript
import { scrubEmployeeForCache, validateScrubbed } from '@ham-agent/shared';
import { prisma } from '@ham-agent/database';
import { logger } from '../lib/logger';

export async function cacheEmployees(employees: any[]) {
  const results = [];

  for (const employee of employees) {
    // Scrub PII before caching
    const scrubbed = scrubEmployeeForCache(employee);

    // Validate scrubbing
    if (!validateScrubbed(scrubbed)) {
      logger.error('PII scrubbing validation failed', { employeeId: employee.id });
      continue;
    }

    // Safe to cache
    const cached = await prisma.employee.upsert({
      where: { id: scrubbed.id },
      create: scrubbed,
      update: scrubbed,
    });

    logger.info('Employee cached with PII scrubbed', {
      employeeId: cached.id,
      // Do NOT log PII fields
    });

    results.push(cached);
  }

  return results;
}
```

## Compliance

This PII scrubbing is required for:

- **GDPR** compliance (right to be forgotten, data minimization)
- **CCPA** compliance (California Consumer Privacy Act)
- **HIPAA** compliance (if health-related data is present)
- **SOC 2** compliance (data security controls)
- **Internal security policies** (principle of least privilege)

## Questions?

For questions about PII scrubbing or to report potential PII leaks, contact the security team.
