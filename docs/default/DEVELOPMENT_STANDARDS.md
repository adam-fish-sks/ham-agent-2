# Development Standards

**Last Updated:** January 8, 2026  
**Status:** Active  
**Applies To:** All code in monorepo

---

## Table of Contents

1. [Code Style](#code-style)
2. [File Organization](#file-organization)
3. [Naming Conventions](#naming-conventions)
4. [TypeScript Standards](#typescript-standards)
5. [React/Next.js Patterns](#reactnextjs-patterns)
6. [Backend Patterns](#backend-patterns)
7. [Database Standards](#database-standards)
8. [Error Handling](#error-handling)
9. [Logging](#logging)
10. [Comments & Documentation](#comments--documentation)
11. [Import Organization](#import-organization)
12. [Testing Standards](#testing-standards)

---

## Code Style

### Automated Formatting

**All code MUST be formatted with Prettier before commit.**

```bash
# Format all files
pnpm format

# Format on save in VS Code (recommended)
# Add to .vscode/settings.json:
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode"
}
```

### ESLint

**All code MUST pass ESLint checks.**

```bash
# Run linting
pnpm lint

# Fix auto-fixable issues
pnpm lint --fix
```

### Line Length

- **Max 100 characters** (Prettier enforced)
- Break long lines logically
- Prefer readability over brevity

### Quotes

- **Single quotes** for strings in TS/JS (Prettier default)
- **Double quotes** for JSX attributes (Prettier default)

```typescript
// ✅ Good
const message = 'Hello world';
<Button text="Click me" />

// ❌ Bad
const message = "Hello world";
<Button text='Click me' />
```

---

## File Organization

### Monorepo Structure

```
apps/
  web/              # Next.js web application
  api/              # Express API server
  worker/           # Background job processor
  desktop/          # Tauri desktop app (if needed)
packages/
  shared/           # Shared utilities, types, constants
  database/         # Prisma schema, migrations, client
```

### Application Structure

#### Next.js (apps/web/src/)

```
app/                    # App Router
  (auth)/              # Route group - auth pages
  (marketing)/         # Route group - public pages
  (dashboard)/         # Route group - protected pages
  api/                 # API routes
components/
  ui/                  # shadcn/ui components
  features/            # Feature-specific components
    users/
      UserList.tsx
      UserCard.tsx
      hooks/
        useUsers.ts
lib/                   # Utilities
  utils.ts
  api-client.ts
hooks/                 # Shared React hooks
types/                 # App-specific types
stores/                # Zustand stores
```

#### Express API (apps/api/src/)

```
index.ts               # Entry point
routes/                # Route handlers
  users.ts
  auth.ts
middleware/            # Express middleware
  auth.ts
  errorHandler.ts
services/              # Business logic
  userService.ts
  emailService.ts
utils/                 # Utilities
types/                 # API-specific types
```

### File Naming

- **Components:** PascalCase (`UserCard.tsx`, `EmailTemplate.tsx`)
- **Utilities:** camelCase (`formatDate.ts`, `apiClient.ts`)
- **Hooks:** camelCase with `use` prefix (`useAuth.ts`, `useLocalStorage.ts`)
- **Types:** PascalCase (`User.ts`, `ApiResponse.ts`)
- **Constants:** UPPER_SNAKE_CASE file or const (`CONSTANTS.ts`, `API_ROUTES.ts`)
- **Tests:** Same as source with `.test.ts` or `.spec.ts` suffix

---

## Naming Conventions

### Variables & Functions

```typescript
// ✅ Good - Descriptive, camelCase
const userCount = 10;
const isAuthenticated = true;
function fetchUserData() {}
function calculateTotalPrice() {}

// ❌ Bad - Unclear, abbreviated
const cnt = 10;
const auth = true;
function fetchData() {}
function calc() {}
```

### Constants

```typescript
// ✅ Good - UPPER_SNAKE_CASE for true constants
const MAX_RETRY_ATTEMPTS = 3;
const API_BASE_URL = 'https://api.example.com';

// ✅ Good - camelCase for config objects
const apiConfig = {
  timeout: 5000,
  retries: 3,
};

// ❌ Bad - Don't uppercase config objects
const API_CONFIG = { timeout: 5000 };
```

### Boolean Variables

**Always use `is`, `has`, `should`, `can`, `will` prefixes**

```typescript
// ✅ Good
const isLoading = true;
const hasPermission = false;
const shouldRefetch = true;
const canEdit = false;
const willExpire = true;

// ❌ Bad
const loading = true;
const permission = false;
const refetch = true;
```

### Functions

**Use verb prefixes for functions**

```typescript
// ✅ Good - Action verbs
function getUser() {}
function createOrder() {}
function updateProfile() {}
function deleteItem() {}
function fetchData() {}
function calculateTotal() {}
function validateEmail() {}
function handleClick() {}

// ❌ Bad - Unclear purpose
function user() {}
function order() {}
function profile() {}
```

### React Components

```typescript
// ✅ Good - PascalCase, descriptive
function UserProfileCard() {}
function EmailNotificationSettings() {}
function DataTable() {}

// ❌ Bad - Vague or abbreviated
function Card() {}
function Settings() {}
function Table() {}
```

### Event Handlers

```typescript
// ✅ Good - handle* prefix
function handleClick() {}
function handleSubmit() {}
function handleUserDelete() {}

// ✅ Good - on* for props
<Button onClick={handleClick} onSubmit={handleSubmit} />

// ❌ Bad - Inconsistent naming
function clickHandler() {}
function onClickButton() {}
```

---

## TypeScript Standards

### Strict Mode

**Always use strict mode.** `tsconfig.json` must include:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

### Type Definitions

**Prefer interfaces for objects, types for unions/intersections**

```typescript
// ✅ Good - Interface for object shape
interface User {
  id: string;
  email: string;
  name: string;
}

// ✅ Good - Type for unions
type Status = 'pending' | 'active' | 'inactive';
type Result = Success | Error;

// ✅ Good - Type for utility types
type PartialUser = Partial<User>;
type ReadonlyUser = Readonly<User>;
```

### Avoid `any`

```typescript
// ❌ Bad - Never use any
function processData(data: any) {}

// ✅ Good - Use unknown and type guard
function processData(data: unknown) {
  if (typeof data === 'object' && data !== null) {
    // Type narrowing
  }
}

// ✅ Good - Use generic
function processData<T>(data: T) {}
```

### Use Type Inference

```typescript
// ✅ Good - Let TypeScript infer
const count = 5;
const items = ['a', 'b', 'c'];
const user = { id: '1', name: 'John' };

// ❌ Bad - Redundant type annotations
const count: number = 5;
const items: string[] = ['a', 'b', 'c'];
```

### Function Return Types

**Always specify return types for exported functions**

```typescript
// ✅ Good - Explicit return type
export function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// ✅ Good - Explicit async return
export async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

// ⚠️ Acceptable for internal functions (but explicit is better)
function helperFunction(x: number) {
  return x * 2;
}
```

### Null/Undefined Handling

```typescript
// ✅ Good - Use optional chaining
const userName = user?.profile?.name;

// ✅ Good - Use nullish coalescing
const displayName = userName ?? 'Guest';

// ✅ Good - Type guard
if (user !== null && user !== undefined) {
  console.log(user.name);
}

// ❌ Bad - Loose equality
if (user != null) {
} // Don't use != or ==
```

---

## React/Next.js Patterns

### Component Structure

```typescript
// ✅ Good - Consistent structure
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import type { User } from '@/types';

interface UserCardProps {
  user: User;
  onEdit?: (user: User) => void;
}

export function UserCard({ user, onEdit }: UserCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  function handleExpand() {
    setIsExpanded(!isExpanded);
  }

  return (
    <div>
      <h3>{user.name}</h3>
      {isExpanded && <p>{user.email}</p>}
      {onEdit && <Button onClick={() => onEdit(user)}>Edit</Button>}
    </div>
  );
}
```

### Props Interfaces

**Always define props interface, never inline**

```typescript
// ✅ Good - Separate interface
interface ButtonProps {
  text: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

export function Button({ text, onClick, variant = 'primary' }: ButtonProps) {
  return <button onClick={onClick}>{text}</button>;
}

// ❌ Bad - Inline types
export function Button({
  text,
  onClick,
}: {
  text: string;
  onClick: () => void;
}) {
  return <button onClick={onClick}>{text}</button>;
}
```

### Server vs Client Components

```typescript
// ✅ Good - Server component (default in Next.js App Router)
// No 'use client' directive
async function UserProfile({ userId }: { userId: string }) {
  const user = await fetchUser(userId); // Direct data fetching
  return <div>{user.name}</div>;
}

// ✅ Good - Client component (needs interactivity)
'use client';

import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

**Rule:** Only use `'use client'` when you need:

- React hooks (useState, useEffect, etc.)
- Browser APIs (localStorage, etc.)
- Event handlers (onClick, onChange, etc.)
- Third-party libraries that use hooks

### Custom Hooks

```typescript
// ✅ Good - Reusable hook with proper typing
export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value: T) => {
    setStoredValue(value);
    window.localStorage.setItem(key, JSON.stringify(value));
  };

  return [storedValue, setValue];
}
```

### Server Actions

```typescript
// ✅ Good - Server action with validation
'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const schema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

export async function createUser(formData: FormData) {
  const data = {
    name: formData.get('name'),
    email: formData.get('email'),
  };

  const result = schema.safeParse(data);
  if (!result.success) {
    return { error: result.error.flatten() };
  }

  await prisma.user.create({ data: result.data });
  revalidatePath('/users');

  return { success: true };
}
```

---

## Backend Patterns

### Route Handler Structure

```typescript
// ✅ Good - Express route with proper error handling
import { Router } from 'express';
import { z } from 'zod';
import { authenticate } from '@/middleware/auth';
import { userService } from '@/services/userService';

const router = Router();

const createUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

router.post('/users', authenticate, async (req, res, next) => {
  try {
    const data = createUserSchema.parse(req.body);
    const user = await userService.createUser(data);
    res.status(201).json({ data: user });
  } catch (error) {
    next(error); // Pass to error handler
  }
});

export default router;
```

### Service Layer

**Always separate business logic from routes**

```typescript
// ✅ Good - Dedicated service file
// services/userService.ts
import { prisma } from '@uplift/database';

export const userService = {
  async createUser(data: { name: string; email: string }) {
    // Check for duplicates
    const existing = await prisma.user.findUnique({
      where: { email: data.email },
    });

    if (existing) {
      throw new Error('User already exists');
    }

    return prisma.user.create({ data });
  },

  async getUserById(id: string) {
    const user = await prisma.user.findUnique({ where: { id } });
    if (!user) {
      throw new Error('User not found');
    }
    return user;
  },
};
```

### API Response Format

**Standardize all API responses**

```typescript
// ✅ Good - Consistent response format
interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// Success response
res.json({
  data: user,
  message: 'User created successfully',
});

// Error response
res.status(400).json({
  error: 'Validation failed',
  message: 'Email is required',
});
```

---

## Database Standards

### Prisma Schema

**Use consistent naming and relationships**

```prisma
// ✅ Good - Clear naming, proper relations
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  posts     Post[]
  profile   Profile?

  @@index([email])
  @@map("users") // Maps to "users" table
}

model Post {
  id        String   @id @default(cuid())
  title     String
  content   String?
  published Boolean  @default(false)
  authorId  String

  author    User     @relation(fields: [authorId], references: [id])

  @@index([authorId])
  @@map("posts")
}
```

### Prisma Queries

```typescript
// ✅ Good - Use select for performance
const user = await prisma.user.findUnique({
  where: { id },
  select: {
    id: true,
    name: true,
    email: true,
    // Only fetch what you need
  },
});

// ✅ Good - Use include for relations
const userWithPosts = await prisma.user.findUnique({
  where: { id },
  include: {
    posts: true,
  },
});

// ❌ Bad - Don't fetch everything
const user = await prisma.user.findUnique({ where: { id } });
```

### Transactions

```typescript
// ✅ Good - Use transactions for multi-step operations
await prisma.$transaction(async (tx) => {
  const user = await tx.user.create({ data: userData });
  await tx.profile.create({
    data: { userId: user.id, ...profileData },
  });
});
```

---

## Error Handling

### Try-Catch Blocks

```typescript
// ✅ Good - Specific error handling
async function fetchUser(id: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    logger.error('Error fetching user', { userId: id, error });
    throw error; // Re-throw or handle appropriately
  }
}
```

### Custom Error Classes

```typescript
// ✅ Good - Typed errors
export class NotFoundError extends Error {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`);
    this.name = 'NotFoundError';
  }
}

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

// Usage
if (!user) {
  throw new NotFoundError('User', userId);
}
```

### Error Boundaries (React)

```typescript
// ✅ Good - Error boundary for graceful failures
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    console.error('ErrorBoundary caught:', error);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong</div>;
    }

    return this.props.children;
  }
}
```

---

## Logging

### Use Pino Logger

```typescript
// ✅ Good - Structured logging
import logger from '@/lib/logger';

logger.info('User created', { userId: user.id, email: user.email });
logger.error('Database error', { error, query });
logger.warn('Rate limit exceeded', { userId, endpoint });
```

### Log Levels

- **error**: Errors that need attention
- **warn**: Warning conditions
- **info**: Informational messages
- **debug**: Debug information (dev only)

### What to Log

```typescript
// ✅ Good - Log important events
logger.info('User authentication successful', { userId });
logger.error('Payment processing failed', { orderId, error });
logger.warn('Slow query detected', { query, duration });

// ❌ Bad - Don't log sensitive data
logger.info('User login', { password: 'secret123' }); // NO!
logger.info('API call', { apiKey: 'sk-xxx' }); // NO!
```

---

## Comments & Documentation

### When to Comment

**Code should be self-documenting. Add comments only when:**

1. **Why, not what:** Explain reasoning, not obvious code
2. **Complex algorithms:** Clarify non-obvious logic
3. **Workarounds:** Explain temporary solutions
4. **Public APIs:** JSDoc for exported functions

### Good Comments

```typescript
// ✅ Good - Explains WHY
// Using setTimeout to avoid race condition with React 18 concurrent rendering
setTimeout(() => setData(newData), 0);

// ✅ Good - Explains complex business logic
// Calculate prorated refund: (days_remaining / total_days) * price
const refund = (daysRemaining / totalDays) * price;

// ✅ Good - Documents workaround
// TODO: Remove this once upstream library fixes the type issue
// @ts-ignore
const result = legacyFunction(data);
```

### Bad Comments

```typescript
// ❌ Bad - States the obvious
// Increment counter by 1
counter++;

// ❌ Bad - Redundant
// Get user by ID
function getUserById(id: string) {}

// ❌ Bad - Outdated/wrong comment
// Returns user object (actually returns array now)
function getUsers() {
  return [];
}
```

### JSDoc for Exported Functions

```typescript
/**
 * Calculates the total price including tax
 * @param price - Base price before tax
 * @param taxRate - Tax rate as decimal (e.g., 0.08 for 8%)
 * @returns Total price including tax
 * @throws {Error} If price or taxRate is negative
 */
export function calculateTotalPrice(price: number, taxRate: number): number {
  if (price < 0 || taxRate < 0) {
    throw new Error('Price and tax rate must be non-negative');
  }
  return price * (1 + taxRate);
}
```

---

## Import Organization

### Import Order

**Always organize imports in this order:**

1. External packages (React, Next.js, third-party)
2. Internal packages (@uplift/shared, @uplift/database)
3. Absolute imports (@/components, @/lib)
4. Relative imports (../, ./)
5. Type imports (last)

```typescript
// ✅ Good - Organized imports
// 1. External
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { z } from 'zod';

// 2. Internal packages
import { prisma } from '@uplift/database';
import { formatDate } from '@uplift/shared';

// 3. Absolute imports
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';

// 4. Relative imports
import { UserCard } from './UserCard';
import { helper } from '../utils';

// 5. Types
import type { User } from '@/types';
import type { ApiResponse } from './types';
```

### Barrel Exports

**Use index.ts for cleaner imports**

```typescript
// components/ui/index.ts
export { Button } from './button';
export { Card } from './card';
export { Dialog } from './dialog';

// Usage
import { Button, Card, Dialog } from '@/components/ui';
```

---

## Testing Standards

### Test File Location

**Co-locate tests with source files**

```
src/
  components/
    UserCard.tsx
    UserCard.test.tsx
  services/
    userService.ts
    userService.test.ts
```

### Test Naming

```typescript
// ✅ Good - Descriptive test names
describe('UserCard', () => {
  it('displays user name and email', () => {});
  it('calls onEdit when edit button is clicked', () => {});
  it('renders null when user is not provided', () => {});
});

// ❌ Bad - Vague test names
describe('UserCard', () => {
  it('works', () => {});
  it('test 1', () => {});
});
```

### Test Coverage

**Minimum coverage requirements:**

- **Critical paths:** 90%+
- **Services/utils:** 80%+
- **UI components:** 60%+

See [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) for details.

---

## Enforcement

### Pre-commit Hooks

**Use Husky to enforce standards:**

```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "pnpm lint && pnpm typecheck"
    }
  }
}
```

### CI Checks

**GitHub Actions must pass:**

- ✅ Prettier formatting
- ✅ ESLint
- ✅ TypeScript compilation
- ✅ Unit tests
- ✅ Build succeeds

### Code Review

**Reviewers must verify:**

- Follows naming conventions
- Proper error handling
- No sensitive data logged
- Tests included
- Comments explain "why"

---

## Questions?

If anything is unclear or you think a standard should change:

1. Discuss in team meeting
2. Propose changes via PR to this document
3. Document decision in [ARCHITECTURE_DECISION_RECORDS.md](./ARCHITECTURE_DECISION_RECORDS.md)

---

**These standards are living documents. Update them as we learn and improve.**
