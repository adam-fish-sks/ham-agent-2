# API Design Guidelines

**Last Updated:** January 8, 2026  
**Status:** Active  
**Purpose:** Ensure consistent, predictable API design across all services

---

## Table of Contents

1. [REST Principles](#rest-principles)
2. [URL Structure](#url-structure)
3. [HTTP Methods](#http-methods)
4. [Request Format](#request-format)
5. [Response Format](#response-format)
6. [Error Handling](#error-handling)
7. [Status Codes](#status-codes)
8. [Pagination](#pagination)
9. [Filtering & Sorting](#filtering--sorting)
10. [Versioning](#versioning)
11. [Authentication](#authentication)
12. [Rate Limiting](#rate-limiting)
13. [Documentation](#documentation)

---

## REST Principles

### Resource-Oriented Design

APIs should be designed around **resources** (nouns), not actions (verbs).

```
✅ Good - Resource-based
GET    /api/users
POST   /api/users
GET    /api/users/123
PUT    /api/users/123
DELETE /api/users/123

❌ Bad - Action-based
POST   /api/getUsers
POST   /api/createUser
POST   /api/updateUser/123
POST   /api/deleteUser/123
```

### Use HTTP Methods Correctly

- **GET:** Retrieve data (safe, idempotent)
- **POST:** Create new resource
- **PUT:** Update entire resource (idempotent)
- **PATCH:** Partial update
- **DELETE:** Remove resource (idempotent)

---

## URL Structure

### Format

```
https://api.example.com/v1/{resource}/{id}/{sub-resource}
```

### Guidelines

**1. Use plural nouns for collections**

```
✅ /api/users
✅ /api/orders
❌ /api/user
❌ /api/order
```

**2. Use kebab-case for multi-word resources**

```
✅ /api/user-profiles
✅ /api/order-items
❌ /api/userProfiles
❌ /api/order_items
```

**3. Use nested resources for relationships**

```
✅ /api/users/123/orders
✅ /api/orders/456/items
❌ /api/orders?userId=123
```

**But don't nest too deeply (max 2 levels):**

```
✅ /api/users/123/orders
❌ /api/users/123/orders/456/items/789/reviews
Better: /api/order-items/789/reviews
```

**4. Use query parameters for filtering, not path segments**

```
✅ /api/users?status=active&role=admin
❌ /api/users/active/admin
```

**5. Keep URLs lowercase**

```
✅ /api/users/123/order-history
❌ /api/Users/123/OrderHistory
```

---

## HTTP Methods

### GET - Retrieve Resources

**Retrieve collection:**

```http
GET /api/users
Response: 200 OK
[
  { "id": "1", "name": "John" },
  { "id": "2", "name": "Jane" }
]
```

**Retrieve single resource:**

```http
GET /api/users/123
Response: 200 OK
{ "id": "123", "name": "John", "email": "john@example.com" }
```

**Rules:**

- Must be safe (no side effects)
- Must be idempotent
- Can be cached
- Never modify data

### POST - Create Resources

```http
POST /api/users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com"
}

Response: 201 Created
Location: /api/users/123
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "createdAt": "2026-01-08T12:00:00Z"
}
```

**Rules:**

- Return `201 Created` on success
- Include `Location` header with new resource URL
- Return created resource in body
- Not idempotent (multiple calls create multiple resources)

### PUT - Replace Entire Resource

```http
PUT /api/users/123
Content-Type: application/json

{
  "name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "555-0100"
}

Response: 200 OK
{
  "id": "123",
  "name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "555-0100",
  "updatedAt": "2026-01-08T12:30:00Z"
}
```

**Rules:**

- Replaces entire resource
- Must be idempotent
- Include all fields (missing fields set to null/default)
- Return `200 OK` or `204 No Content`

### PATCH - Partial Update

```http
PATCH /api/users/123
Content-Type: application/json

{
  "phone": "555-0100"
}

Response: 200 OK
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "555-0100",
  "updatedAt": "2026-01-08T12:30:00Z"
}
```

**Rules:**

- Only include fields to update
- Should be idempotent
- Return full resource or just updated fields
- Return `200 OK`

### DELETE - Remove Resource

```http
DELETE /api/users/123

Response: 204 No Content
```

**Rules:**

- Return `204 No Content` (no body)
- Must be idempotent
- Return `404` if already deleted
- Consider soft deletes for audit trail

---

## Request Format

### Content Type

**Always use JSON for request/response bodies**

```http
Content-Type: application/json
```

### Request Body Structure

**Simple create/update:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

**Nested relationships:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "address": {
    "street": "123 Main St",
    "city": "Springfield",
    "zip": "12345"
  }
}
```

**Arrays:**

```json
{
  "name": "Order #123",
  "items": [
    { "productId": "p1", "quantity": 2 },
    { "productId": "p2", "quantity": 1 }
  ]
}
```

### Field Naming

**Use camelCase for JSON fields**

```json
✅ Good
{
  "firstName": "John",
  "lastName": "Doe",
  "emailAddress": "john@example.com"
}

❌ Bad - snake_case
{
  "first_name": "John",
  "last_name": "Doe",
  "email_address": "john@example.com"
}

❌ Bad - PascalCase
{
  "FirstName": "John",
  "LastName": "Doe"
}
```

### Required vs Optional Fields

Document which fields are required:

```typescript
// API documentation
interface CreateUserRequest {
  name: string; // required
  email: string; // required
  phone?: string; // optional
  address?: Address; // optional
}
```

---

## Response Format

### Standard Response Envelope

**Success response with data:**

```json
{
  "data": {
    "id": "123",
    "name": "John Doe"
  }
}
```

**Success response with collection:**

```json
{
  "data": [
    { "id": "1", "name": "John" },
    { "id": "2", "name": "Jane" }
  ],
  "meta": {
    "total": 2,
    "page": 1,
    "pageSize": 20
  }
}
```

**Success response with message:**

```json
{
  "data": { "id": "123" },
  "message": "User created successfully"
}
```

### Timestamps

**Always use ISO 8601 format (UTC)**

```json
{
  "createdAt": "2026-01-08T12:00:00.000Z",
  "updatedAt": "2026-01-08T15:30:00.000Z"
}
```

### Null vs Omitted Fields

**Be consistent:**

```json
✅ Option 1: Include null fields
{
  "name": "John",
  "phone": null,
  "address": null
}

✅ Option 2: Omit null fields
{
  "name": "John"
}

❌ Inconsistent
{
  "name": "John",
  "phone": null
  // address omitted
}
```

**Recommendation:** Omit null fields to reduce payload size.

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      },
      {
        "field": "age",
        "message": "Must be at least 18"
      }
    ]
  }
}
```

### Error Structure

```typescript
interface ErrorResponse {
  error: {
    code: string; // Machine-readable error code
    message: string; // Human-readable message
    details?: ErrorDetail[]; // Optional field-level errors
    requestId?: string; // For debugging/support
  };
}

interface ErrorDetail {
  field: string;
  message: string;
}
```

### Error Codes

**Use consistent, descriptive error codes:**

```typescript
// Authentication/Authorization
'UNAUTHORIZED'; // 401 - Not authenticated
'FORBIDDEN'; // 403 - Authenticated but no permission
'TOKEN_EXPIRED'; // 401 - Auth token expired

// Validation
'VALIDATION_ERROR'; // 400 - Input validation failed
'MISSING_FIELD'; // 400 - Required field missing
'INVALID_FORMAT'; // 400 - Field format invalid

// Resources
'NOT_FOUND'; // 404 - Resource not found
'ALREADY_EXISTS'; // 409 - Resource already exists
'CONFLICT'; // 409 - State conflict

// Server
'INTERNAL_ERROR'; // 500 - Unexpected server error
'SERVICE_UNAVAILABLE'; // 503 - Temporary unavailability

// Rate Limiting
'RATE_LIMIT_EXCEEDED'; // 429 - Too many requests
```

### Examples

**Validation error:**

```http
POST /api/users
{
  "email": "invalid-email"
}

Response: 400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      },
      {
        "field": "name",
        "message": "Name is required"
      }
    ]
  }
}
```

**Not found:**

```http
GET /api/users/999

Response: 404 Not Found
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}
```

**Authorization error:**

```http
DELETE /api/users/123

Response: 403 Forbidden
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to delete this user"
  }
}
```

---

## Status Codes

### Use Standard HTTP Status Codes

**Success (2xx)**

- `200 OK` - Request succeeded (GET, PUT, PATCH)
- `201 Created` - Resource created (POST)
- `204 No Content` - Success with no response body (DELETE)

**Client Error (4xx)**

- `400 Bad Request` - Invalid input/validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Authenticated but no permission
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource conflict (duplicate, state)
- `422 Unprocessable Entity` - Validation error (alternative to 400)
- `429 Too Many Requests` - Rate limit exceeded

**Server Error (5xx)**

- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Upstream service error
- `503 Service Unavailable` - Temporary unavailability
- `504 Gateway Timeout` - Upstream timeout

### Status Code Decision Tree

```
Request received
  ├─ Authentication valid?
  │   └─ No → 401 Unauthorized
  │
  ├─ Authorization permitted?
  │   └─ No → 403 Forbidden
  │
  ├─ Input valid?
  │   └─ No → 400 Bad Request
  │
  ├─ Resource exists? (for GET/PUT/PATCH/DELETE)
  │   └─ No → 404 Not Found
  │
  ├─ Resource conflict? (duplicate, wrong state)
  │   └─ Yes → 409 Conflict
  │
  ├─ Rate limit exceeded?
  │   └─ Yes → 429 Too Many Requests
  │
  ├─ Server error?
  │   └─ Yes → 500 Internal Server Error
  │
  └─ Success
      ├─ Created → 201 Created
      ├─ No content → 204 No Content
      └─ Default → 200 OK
```

---

## Pagination

### Offset-Based Pagination (Simple)

**Request:**

```http
GET /api/users?page=2&pageSize=20
```

**Response:**

```json
{
  "data": [...],
  "meta": {
    "total": 150,
    "page": 2,
    "pageSize": 20,
    "totalPages": 8
  }
}
```

**Query Parameters:**

- `page` - Page number (1-indexed)
- `pageSize` or `limit` - Items per page (default: 20, max: 100)

### Cursor-Based Pagination (For large datasets)

**Request:**

```http
GET /api/users?cursor=eyJpZCI6MTIzfQ&limit=20
```

**Response:**

```json
{
  "data": [...],
  "meta": {
    "nextCursor": "eyJpZCI6MTQzfQ",
    "hasMore": true
  }
}
```

**When to use:**

- Large datasets (10k+ records)
- Real-time data (where total count changes)
- Performance critical

### Default Pagination

**Always paginate collections** (prevent accidental full table scans):

```typescript
// Default pagination
const DEFAULT_PAGE_SIZE = 20;
const MAX_PAGE_SIZE = 100;

// Apply even if not requested
GET / api / users;
// Automatically applies ?page=1&pageSize=20
```

---

## Filtering & Sorting

### Filtering

**Use query parameters for filtering:**

```http
# Single filter
GET /api/users?status=active

# Multiple filters (AND)
GET /api/users?status=active&role=admin

# Multiple values (OR)
GET /api/users?role=admin,manager

# Range filters
GET /api/orders?createdAfter=2026-01-01&createdBefore=2026-01-31

# Search
GET /api/users?search=john
```

### Sorting

**Use `sort` parameter with field name:**

```http
# Ascending
GET /api/users?sort=name

# Descending (use minus prefix)
GET /api/users?sort=-createdAt

# Multiple fields
GET /api/users?sort=role,-createdAt
```

### Field Selection (Sparse Fieldsets)

**Allow clients to specify fields to reduce payload:**

```http
GET /api/users?fields=id,name,email
```

Response:

```json
{
  "data": [{ "id": "1", "name": "John", "email": "john@example.com" }]
}
```

---

## Versioning

### URL Path Versioning (Recommended)

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**Pros:**

- Clear and explicit
- Easy to route
- Supports multiple versions simultaneously

**Guidelines:**

- Start at `v1`
- Increment for breaking changes only
- Support previous version for 6-12 months
- Deprecation warnings in response headers

```http
Response Headers:
Deprecation: true
Sunset: Wed, 01 Jul 2026 23:59:59 GMT
Link: </v2/users>; rel="successor-version"
```

### When to Version

**Increment version for breaking changes:**

- Removing fields
- Renaming fields
- Changing field types
- Changing URL structure
- Changing authentication

**Don't increment for:**

- Adding optional fields
- Adding new endpoints
- Bug fixes
- Performance improvements

---

## Authentication

### Bearer Token (Recommended)

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Use JWT tokens from Azure AD/Entra ID:**

- Include in Authorization header
- Validate signature
- Check expiration
- Verify claims (audience, issuer)

### API Keys (For service-to-service)

```http
X-API-Key: sk_live_abc123def456
```

**Only for:**

- Server-to-server communication
- Internal services
- Webhooks

**Never for:**

- Browser/client apps (use OAuth)
- Embedding in mobile apps

---

## Rate Limiting

### Standard Rate Limits

**Authenticated users:**

- 1000 requests per hour per user
- 60 requests per minute per user

**Unauthenticated requests:**

- 100 requests per hour per IP
- 10 requests per minute per IP

### Response Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641024000
```

### Rate Limit Exceeded

```http
Response: 429 Too Many Requests
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 1 hour.",
    "retryAfter": 3600
  }
}
```

---

## Documentation

### OpenAPI/Swagger

**Document all endpoints using OpenAPI 3.0:**

```yaml
openapi: 3.0.0
info:
  title: Application API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

### Endpoint Documentation Requirements

Each endpoint must document:

1. **Purpose** - What it does
2. **Authentication** - Required or optional
3. **Parameters** - Query params, path params, body
4. **Request example** - Sample request
5. **Response example** - Sample successful response
6. **Error examples** - Common error responses
7. **Rate limits** - Specific limits if different from default

### Example Documentation

```typescript
/**
 * GET /api/users
 *
 * List all users with pagination
 *
 * Authentication: Required (Bearer token)
 *
 * Query Parameters:
 *   - page (number, default: 1): Page number
 *   - pageSize (number, default: 20, max: 100): Items per page
 *   - status (string, optional): Filter by status (active, inactive)
 *   - sort (string, optional): Sort field (e.g., 'name', '-createdAt')
 *
 * Response: 200 OK
 * {
 *   "data": [
 *     { "id": "1", "name": "John", "email": "john@example.com" }
 *   ],
 *   "meta": {
 *     "total": 150,
 *     "page": 1,
 *     "pageSize": 20
 *   }
 * }
 *
 * Errors:
 *   - 401: Unauthorized (missing/invalid token)
 *   - 429: Rate limit exceeded
 */
```

---

## Testing APIs

### Required Tests

1. **Happy path** - Successful request/response
2. **Validation** - Invalid input handling
3. **Authentication** - Missing/invalid credentials
4. **Authorization** - Insufficient permissions
5. **Not found** - Non-existent resources
6. **Edge cases** - Empty lists, max limits, etc.

### Example Test

```typescript
describe('GET /api/users/:id', () => {
  it('returns user when id exists', async () => {
    const res = await request(app)
      .get('/api/users/123')
      .set('Authorization', `Bearer ${token}`)
      .expect(200);

    expect(res.body.data).toMatchObject({
      id: '123',
      name: expect.any(String),
      email: expect.any(String),
    });
  });

  it('returns 404 when user not found', async () => {
    const res = await request(app)
      .get('/api/users/999')
      .set('Authorization', `Bearer ${token}`)
      .expect(404);

    expect(res.body.error.code).toBe('NOT_FOUND');
  });

  it('returns 401 when not authenticated', async () => {
    await request(app).get('/api/users/123').expect(401);
  });
});
```

---

## Quick Reference Checklist

When creating a new API endpoint, verify:

- [ ] Uses appropriate HTTP method (GET, POST, PUT, PATCH, DELETE)
- [ ] URL follows REST conventions (plural nouns, kebab-case)
- [ ] Accepts and returns JSON with proper Content-Type
- [ ] Uses standard HTTP status codes
- [ ] Returns consistent response format (with `data` envelope)
- [ ] Includes proper error handling with error codes
- [ ] Validates input with clear error messages
- [ ] Implements pagination for collections
- [ ] Supports filtering and sorting where appropriate
- [ ] Requires authentication where needed
- [ ] Enforces authorization rules
- [ ] Respects rate limits
- [ ] Has OpenAPI/Swagger documentation
- [ ] Includes unit and integration tests
- [ ] Logs important events (not sensitive data)
- [ ] Returns appropriate timestamps in ISO 8601 format

---

**Questions or suggestions? Open a PR to improve these guidelines!**
