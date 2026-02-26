# Testing Strategy

**Last Updated:** January 8, 2026  
**Status:** Active  
**Purpose:** Define testing approach, coverage requirements, and best practices

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Testing Pyramid](#testing-pyramid)
3. [Coverage Requirements](#coverage-requirements)
4. [Unit Testing](#unit-testing)
5. [Integration Testing](#integration-testing)
6. [E2E Testing](#e2e-testing)
7. [Testing Tools](#testing-tools)
8. [Best Practices](#best-practices)
9. [CI/CD Integration](#cicd-integration)

---

## Testing Philosophy

### Core Principles

1. **Test behavior, not implementation**
   - Test what users care about
   - Don't test internal implementation details
   - Tests should survive refactoring

2. **Write tests first (TDD encouraged)**
   - Clarifies requirements
   - Better design
   - Built-in regression tests

3. **Fast feedback**
   - Unit tests run in milliseconds
   - Quick iteration cycles
   - Fail fast

4. **Confidence over coverage**
   - 100% coverage ≠ bug-free
   - Focus on critical paths
   - Meaningful assertions

---

## Testing Pyramid

```
        /\
       /E2E\       ← Few, slow, expensive
      /─────\
     /  Int  \     ← Some, moderate
    /────────\
   /   Unit   \    ← Many, fast, cheap
  /────────────\
```

### Distribution (Guidelines)

- **Unit Tests:** 70% - Fast, isolated, many
- **Integration Tests:** 20% - API/DB interactions
- **E2E Tests:** 10% - Critical user flows

---

## Coverage Requirements

### Minimum Coverage

| Type | Target | Critical Paths |
|------|--------|----------------|
| **Services/Utils** | 80% | 90%+ |
| **API Endpoints** | 75% | 90%+ |
| **Components** | 60% | 80%+ |
| **Overall** | 70% | - |

### What Must Be Tested

**Always test:**
- ✅ Business logic
- ✅ Data transformations
- ✅ Validation logic
- ✅ Error handling
- ✅ Security checks
- ✅ Critical user paths

**Can skip:**
- ❌ Third-party libraries
- ❌ Simple getters/setters
- ❌ Generated code (Prisma client)
- ❌ Configuration files

---

## Unit Testing

### What to Unit Test

**Test individual functions/methods in isolation:**
- Pure functions
- Business logic
- Utilities
- Validators
- Formatters

### Unit Test Structure

```typescript
describe('calculateDiscount', () => {
  it('applies 10% discount for standard items', () => {
    const result = calculateDiscount(100, 'standard');
    expect(result).toBe(90);
  });

  it('applies 20% discount for premium items', () => {
    const result = calculateDiscount(100, 'premium');
    expect(result).toBe(80);
  });

  it('throws error for negative price', () => {
    expect(() => calculateDiscount(-10, 'standard')).toThrow('Price must be positive');
  });

  it('returns original price for invalid tier', () => {
    const result = calculateDiscount(100, 'invalid');
    expect(result).toBe(100);
  });
});
```

### Mock External Dependencies

```typescript
import { vi } from 'vitest';
import { sendEmail } from './emailService';
import { createUser } from './userService';

// Mock external service
vi.mock('./emailService');

describe('createUser', () => {
  it('sends welcome email after user creation', async () => {
    const mockSendEmail = vi.mocked(sendEmail);
    
    await createUser({ name: 'John', email: 'john@example.com' });
    
    expect(mockSendEmail).toHaveBeenCalledWith(
      'john@example.com',
      'Welcome to our platform'
    );
  });
});
```

### Testing Async Code

```typescript
describe('fetchUser', () => {
  it('returns user data when successful', async () => {
    const user = await fetchUser('123');
    
    expect(user).toMatchObject({
      id: '123',
      name: expect.any(String),
      email: expect.any(String),
    });
  });

  it('throws error when user not found', async () => {
    await expect(fetchUser('999')).rejects.toThrow('User not found');
  });
});
```

---

## Integration Testing

### What to Integration Test

**Test interactions between components:**
- API endpoints with database
- Service layer with database
- External API integrations
- Authentication flows

### API Integration Tests

```typescript
import request from 'supertest';
import { app } from '../src/app';
import { prisma } from '@uplift/database';

describe('POST /api/users', () => {
  // Setup: Clean database before each test
  beforeEach(async () => {
    await prisma.user.deleteMany();
  });

  it('creates user with valid data', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({
        name: 'John Doe',
        email: 'john@example.com',
      })
      .expect(201);

    expect(res.body.data).toMatchObject({
      id: expect.any(String),
      name: 'John Doe',
      email: 'john@example.com',
    });

    // Verify in database
    const user = await prisma.user.findUnique({
      where: { email: 'john@example.com' },
    });
    expect(user).toBeTruthy();
  });

  it('returns 400 for invalid email', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({
        name: 'John Doe',
        email: 'invalid-email',
      })
      .expect(400);

    expect(res.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('returns 409 for duplicate email', async () => {
    // Create first user
    await request(app)
      .post('/api/users')
      .send({
        name: 'John Doe',
        email: 'john@example.com',
      });

    // Try to create duplicate
    const res = await request(app)
      .post('/api/users')
      .send({
        name: 'Jane Doe',
        email: 'john@example.com',
      })
      .expect(409);

    expect(res.body.error.code).toBe('ALREADY_EXISTS');
  });
});
```

### Database Testing

```typescript
describe('UserService', () => {
  beforeEach(async () => {
    await prisma.user.deleteMany();
  });

  describe('createUser', () => {
    it('creates user in database', async () => {
      const user = await userService.createUser({
        name: 'John',
        email: 'john@example.com',
      });

      expect(user.id).toBeDefined();
      
      const dbUser = await prisma.user.findUnique({
        where: { id: user.id },
      });
      expect(dbUser).toBeTruthy();
    });

    it('hashes password before storing', async () => {
      const user = await userService.createUser({
        name: 'John',
        email: 'john@example.com',
        password: 'password123',
      });

      const dbUser = await prisma.user.findUnique({
        where: { id: user.id },
      });
      
      // Password should be hashed, not plain text
      expect(dbUser.password).not.toBe('password123');
      expect(dbUser.password.startsWith('$2')).toBe(true);
    });
  });
});
```

---

## E2E Testing

### What to E2E Test

**Test critical user journeys:**
- User registration/login
- Core workflows
- Payment processing
- Critical business flows

**Keep E2E tests minimal** - they're slow and fragile.

### E2E Test Example (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('User Authentication', () => {
  test('user can sign up and log in', async ({ page }) => {
    // Navigate to signup
    await page.goto('/signup');

    // Fill signup form
    await page.fill('[name="name"]', 'John Doe');
    await page.fill('[name="email"]', 'john@example.com');
    await page.fill('[name="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Welcome, John');

    // Log out
    await page.click('[data-testid="user-menu"]');
    await page.click('text=Log out');

    // Should redirect to homepage
    await expect(page).toHaveURL('/');

    // Log back in
    await page.goto('/login');
    await page.fill('[name="email"]', 'john@example.com');
    await page.fill('[name="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');

    // Should be back at dashboard
    await expect(page).toHaveURL('/dashboard');
  });
});
```

---

## Testing Tools

### Unit & Integration Tests

**Vitest** (primary test runner)

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('MyComponent', () => {
  it('renders correctly', () => {
    // Test
  });
});
```

**Why Vitest:**
- Fast (Vite-powered)
- Jest-compatible API
- Native TypeScript support
- Watch mode
- Coverage built-in

### API Testing

**Supertest** (HTTP assertions)

```typescript
import request from 'supertest';

await request(app)
  .post('/api/users')
  .send({ name: 'John' })
  .expect(201)
  .expect('Content-Type', /json/);
```

### E2E Testing

**Playwright** (when needed)

```bash
# Install
pnpm add -D @playwright/test

# Run tests
pnpm playwright test

# UI mode
pnpm playwright test --ui
```

---

## Best Practices

### Test Organization

**Co-locate tests with code:**

```
src/
  services/
    userService.ts
    userService.test.ts
  utils/
    formatDate.ts
    formatDate.test.ts
```

### Test Naming

**Use descriptive names:**

```typescript
✅ Good
it('returns 404 when user does not exist')
it('sends email after user creation')
it('calculates discount for premium members')

❌ Bad
it('works')
it('test user')
it('should work correctly')
```

### AAA Pattern (Arrange, Act, Assert)

```typescript
it('calculates total with tax', () => {
  // Arrange - Setup test data
  const price = 100;
  const taxRate = 0.08;

  // Act - Execute the code
  const total = calculateTotal(price, taxRate);

  // Assert - Verify result
  expect(total).toBe(108);
});
```

### One Assertion Per Test (Guideline)

```typescript
✅ Good - Focused tests
it('returns user name', () => {
  const user = getUser();
  expect(user.name).toBe('John');
});

it('returns user email', () => {
  const user = getUser();
  expect(user.email).toBe('john@example.com');
});

⚠️ Acceptable - Related assertions
it('returns complete user object', () => {
  const user = getUser();
  expect(user).toMatchObject({
    name: 'John',
    email: 'john@example.com',
    id: expect.any(String),
  });
});
```

### Test Data Management

**Use factories for test data:**

```typescript
// test/factories/userFactory.ts
export function createUser(overrides = {}) {
  return {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    createdAt: new Date(),
    ...overrides,
  };
}

// Usage
it('handles admin users', () => {
  const admin = createUser({ role: 'admin' });
  expect(isAdmin(admin)).toBe(true);
});
```

### Cleanup

**Always clean up after tests:**

```typescript
describe('Database tests', () => {
  beforeEach(async () => {
    await prisma.user.deleteMany();
  });

  afterEach(async () => {
    await prisma.user.deleteMany();
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });
});
```

---

## React Component Testing

### Testing Library

**React Testing Library** (user-centric testing)

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  it('displays user name and email', () => {
    render(<UserCard user={{ name: 'John', email: 'john@example.com' }} />);
    
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('calls onEdit when edit button clicked', () => {
    const handleEdit = vi.fn();
    render(<UserCard user={{ name: 'John' }} onEdit={handleEdit} />);
    
    fireEvent.click(screen.getByRole('button', { name: /edit/i }));
    
    expect(handleEdit).toHaveBeenCalledTimes(1);
  });

  it('expands details when clicked', async () => {
    render(<UserCard user={{ name: 'John', bio: 'Developer' }} />);
    
    // Details hidden initially
    expect(screen.queryByText('Developer')).not.toBeInTheDocument();
    
    // Click to expand
    fireEvent.click(screen.getByText('John'));
    
    // Details now visible
    await waitFor(() => {
      expect(screen.getByText('Developer')).toBeInTheDocument();
    });
  });
});
```

### Mocking Next.js

```typescript
// Mock useRouter
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => '/test',
}));

// Mock Next Image
vi.mock('next/image', () => ({
  default: (props: any) => <img {...props} />,
}));
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v2
      
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      
      - run: pnpm install
      
      - run: pnpm turbo test
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

### Coverage Reports

```bash
# Generate coverage
pnpm test --coverage

# View report
open coverage/index.html

# Check thresholds
pnpm test --coverage --coverage-thresholds='{
  "branches": 70,
  "functions": 70,
  "lines": 70,
  "statements": 70
}'
```

---

## Performance Testing

### Load Testing (when needed)

```typescript
// Use k6 or artillery for load testing
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 100, // 100 virtual users
  duration: '30s',
};

export default function() {
  const res = http.get('https://api.example.com/users');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
}
```

---

## Common Patterns

### Testing Async Operations

```typescript
it('fetches user data', async () => {
  const user = await fetchUser('123');
  expect(user.id).toBe('123');
});

it('handles fetch error', async () => {
  await expect(fetchUser('invalid')).rejects.toThrow();
});
```

### Testing Promises

```typescript
it('resolves with user data', () => {
  return expect(fetchUser('123')).resolves.toMatchObject({
    id: '123',
  });
});
```

### Testing Timers

```typescript
it('calls function after delay', () => {
  vi.useFakeTimers();
  const callback = vi.fn();
  
  setTimeout(callback, 1000);
  
  vi.advanceTimersByTime(1000);
  expect(callback).toHaveBeenCalled();
  
  vi.useRealTimers();
});
```

---

## What Not to Test

**Don't test:**
- Framework code (React, Next.js)
- Third-party libraries
- Constants/configuration
- Getters/setters without logic
- Type definitions
- Auto-generated code

**Do test:**
- Your business logic
- Edge cases
- Error handling
- User interactions
- API contracts

---

## Troubleshooting Tests

### Flaky Tests

**Common causes:**
- Timing issues (use `waitFor`)
- Test interdependence (isolate tests)
- External dependencies (mock them)
- Race conditions (use proper cleanup)

### Slow Tests

**Solutions:**
- Mock external calls
- Use test database
- Parallelize tests
- Optimize setup/teardown

### Hard to Test

**Refactor for testability:**
- Extract functions
- Inject dependencies
- Use pure functions
- Avoid side effects

---

## Summary

**Good tests:**
- ✅ Fast and reliable
- ✅ Test behavior, not implementation
- ✅ Easy to understand
- ✅ Catch bugs early
- ✅ Give confidence to refactor

**Remember:**
- Tests are code too (maintain them)
- Coverage is a guide, not a goal
- Write tests you would want to debug
- Test critical paths first

---

**Questions? Improve this strategy via PR!**
