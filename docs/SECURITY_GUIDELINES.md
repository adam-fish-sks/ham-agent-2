# Security Guidelines

**Last Updated:** January 8, 2026  
**Status:** Active  
**Criticality:** HIGH - Non-negotiable security requirements

---

## Table of Contents

1. [Security Principles](#security-principles)
2. [Authentication & Authorization](#authentication--authorization)
3. [Secrets Management](#secrets-management)
4. [Input Validation](#input-validation)
5. [Data Protection](#data-protection)
6. [API Security](#api-security)
7. [Frontend Security](#frontend-security)
8. [Database Security](#database-security)
9. [Dependency Security](#dependency-security)
10. [Security Checklist](#security-checklist)

---

## Security Principles

### Defense in Depth

**Layer security controls:**

- Assume any layer can be breached
- Multiple layers of protection
- No single point of failure

### Least Privilege

**Grant minimum necessary access:**

- Users: Only what they need
- Services: Scoped permissions
- Tokens: Limited scope and duration

### Secure by Default

**Security is not optional:**

- All routes require auth (opt-out, not opt-in)
- All inputs are validated
- All outputs are sanitized
- HTTPS everywhere

### Fail Securely

**Errors should not expose information:**

- Generic error messages to users
- Detailed logs internally only
- Fail closed, not open

---

## Authentication & Authorization

### Azure AD / Entra ID (Primary)

**Use Microsoft Authentication Library (MSAL):**

```typescript
import { PublicClientApplication } from '@azure/msal-browser';

const msalConfig = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_AD_CLIENT_ID!,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: process.env.NEXT_PUBLIC_REDIRECT_URI,
  },
};

const msalInstance = new PublicClientApplication(msalConfig);
```

### Token Validation

**Always validate JWT tokens:**

```typescript
import jwt from 'jsonwebtoken';

export function authenticate(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_PUBLIC_KEY!);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Authorization Checks

**Verify permissions before actions:**

```typescript
export function requireRole(role: string) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    if (!req.user.roles?.includes(role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
}

// Usage
router.delete('/users/:id', authenticate, requireRole('admin'), deleteUser);
```

### Session Management

**Secure session handling:**

- Use httpOnly cookies for session tokens
- Set secure flag (HTTPS only)
- Set SameSite=Strict to prevent CSRF
- Rotate sessions on privilege escalation
- Implement session timeout

```typescript
res.cookie('sessionToken', token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict',
  maxAge: 24 * 60 * 60 * 1000, // 24 hours
});
```

---

## Secrets Management

### NEVER Commit Secrets

**Never commit to Git:**

- ❌ Passwords
- ❌ API keys
- ❌ Private keys
- ❌ Connection strings
- ❌ Encryption keys
- ❌ Certificates

### Use Environment Variables

**All secrets in environment variables:**

```bash
# .env.local (never committed)
DATABASE_URL="postgresql://..."
AZURE_AD_CLIENT_SECRET="..."
ENCRYPTION_KEY="..."
API_KEY="..."
```

```typescript
// Access in code
const apiKey = process.env.API_KEY;

// Validate at startup
if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL is required');
}
```

### Azure Key Vault (Production)

**Store secrets in Key Vault:**

```typescript
import { SecretClient } from '@azure/keyvault-secrets';
import { DefaultAzureCredential } from '@azure/identity';

const credential = new DefaultAzureCredential();
const client = new SecretClient(process.env.AZURE_KEYVAULT_URI!, credential);

// Retrieve secret
const secret = await client.getSecret('database-password');
const password = secret.value;
```

### .env.example

**Provide template (no real values):**

```bash
# .env.example (committed)
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
AZURE_AD_CLIENT_ID="your-client-id-here"
AZURE_AD_CLIENT_SECRET="your-secret-here"
ENCRYPTION_KEY="32-character-key-for-aes-256"
```

### Secrets in CI/CD

**Use GitHub Secrets:**

- Settings → Secrets → Actions
- Access as: `${{ secrets.SECRET_NAME }}`
- Never print secrets in logs

---

## Input Validation

### Validate All Inputs

**Never trust user input:**

```typescript
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(18).max(120),
  role: z.enum(['user', 'admin']),
});

router.post('/users', async (req, res) => {
  const result = createUserSchema.safeParse(req.body);

  if (!result.success) {
    return res.status(400).json({
      error: 'Validation failed',
      details: result.error.flatten(),
    });
  }

  const user = await createUser(result.data);
  res.json({ data: user });
});
```

### SQL Injection Prevention

**Use Prisma (parameterized queries):**

```typescript
✅ Good - Prisma (safe)
await prisma.user.findMany({
  where: { email: userInput },
});

❌ Bad - Raw SQL with concatenation
await prisma.$queryRaw`SELECT * FROM users WHERE email = '${userInput}'`;

✅ Good - Parameterized raw query
await prisma.$queryRaw`SELECT * FROM users WHERE email = ${userInput}`;
```

### XSS Prevention

**Sanitize HTML output:**

```typescript
import DOMPurify from 'dompurify';

// Sanitize user-generated HTML
const clean = DOMPurify.sanitize(dirtyHtml);

// In React
<div dangerouslySetInnerHTML={{ __html: clean }} />
```

**Use JSX by default (auto-escapes):**

```typescript
✅ Good - Auto-escaped
<p>{userInput}</p>

❌ Bad - Can inject HTML
<p dangerouslySetInnerHTML={{ __html: userInput }} />
```

### File Upload Validation

**Validate uploaded files:**

```typescript
const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
const maxSize = 5 * 1024 * 1024; // 5MB

function validateFile(file: File) {
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Invalid file type');
  }

  if (file.size > maxSize) {
    throw new Error('File too large');
  }

  return true;
}
```

### Command Injection Prevention

**Never pass user input to shell commands:**

```typescript
❌ Bad - Command injection risk
exec(`convert ${userFilename} output.png`);

✅ Good - Use libraries, not shell
import sharp from 'sharp';
await sharp(userFile).toFile('output.png');
```

---

## Data Protection

### Encryption at Rest

**Sensitive data must be encrypted:**

- Database: Azure PostgreSQL (automatic encryption)
- Storage: Azure Blob Storage (automatic encryption)
- Backups: Encrypted by default

### Encryption in Transit

**Always use HTTPS:**

- Frontend: HTTPS only
- API: HTTPS only
- Websockets: WSS only

```typescript
// Enforce HTTPS in production
if (process.env.NODE_ENV === 'production' && req.protocol !== 'https') {
  return res.redirect(`https://${req.hostname}${req.url}`);
}
```

### Encrypt Sensitive Fields

**Encrypt PII in database:**

```typescript
import crypto from 'crypto';

const algorithm = 'aes-256-gcm';
const key = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex');

export function encrypt(text: string): string {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, key, iv);

  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  const authTag = cipher.getAuthTag();

  return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
}

export function decrypt(encrypted: string): string {
  const [ivHex, authTagHex, encryptedText] = encrypted.split(':');

  const iv = Buffer.from(ivHex, 'hex');
  const authTag = Buffer.from(authTagHex, 'hex');

  const decipher = crypto.createDecipheriv(algorithm, key, iv);
  decipher.setAuthTag(authTag);

  let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
}
```

### Password Hashing

**Use bcrypt for passwords:**

```typescript
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

// Usage
const hashedPassword = await hashPassword('user-password');
await prisma.user.create({
  data: { email, password: hashedPassword },
});
```

### PII Handling

**Personally Identifiable Information (PII):**

- Encrypt in database
- Log only IDs, never PII
- Mask in error messages
- GDPR compliance (right to delete)

```typescript
// Don't log PII
❌ logger.error('Login failed', { email: user.email });
✅ logger.error('Login failed', { userId: user.id });

// Mask sensitive data
function maskEmail(email: string): string {
  const [name, domain] = email.split('@');
  return `${name[0]}***@${domain}`;
}
```

---

## API Security

### Rate Limiting

**Prevent abuse:**

```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  message: 'Too many requests',
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api/', limiter);

// Stricter for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
});

app.use('/api/auth/', authLimiter);
```

### CORS Configuration

**Restrict origins:**

```typescript
import cors from 'cors';

const allowedOrigins = ['https://app.example.com', 'https://admin.example.com'];

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true,
  })
);
```

### Security Headers

**Use Helmet:**

```typescript
import helmet from 'helmet';

app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'unsafe-inline'"],
        styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
        fontSrc: ["'self'", 'https://fonts.gstatic.com'],
        imgSrc: ["'self'", 'data:', 'https:'],
        connectSrc: ["'self'", 'https://*.example.com'],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true,
    },
  })
);
```

### API Versioning

**Never break existing clients:**

- Version APIs (/v1, /v2)
- Deprecate gracefully
- Support old version for 6-12 months

---

## Frontend Security

### Content Security Policy

**Restrict resource loading:**

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self' data:;
      connect-src 'self' https://*.example.com;
    `
      .replace(/\s{2,}/g, ' ')
      .trim(),
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};
```

### Token Storage

**Never store sensitive tokens in localStorage:**

```typescript
❌ Bad - XSS vulnerable
localStorage.setItem('token', accessToken);

✅ Good - httpOnly cookie (set by server)
// Server sets cookie
res.cookie('token', accessToken, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
});

// Client can't access (XSS protection)
```

### Form Security

**CSRF protection:**

```typescript
// Use double submit cookie pattern
import csrf from 'csurf';

const csrfProtection = csrf({ cookie: true });

app.use(csrfProtection);

app.get('/form', (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});

app.post('/submit', csrfProtection, (req, res) => {
  // Process form
});
```

---

## Database Security

### Connection Security

**Use SSL/TLS:**

```typescript
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
  sslmode  = "require"
}
```

### Least Privilege Access

**Database users have minimum permissions:**

- Application user: CRUD only
- Admin user: Schema changes
- Read-only user: SELECT only

### Backup Security

**Encrypt backups:**

- Automated backups encrypted
- Store in secure location (Azure Blob)
- Test restore procedures
- Retention policy defined

### Audit Logging

**Track sensitive operations:**

```prisma
model AuditLog {
  id        String   @id @default(cuid())
  userId    String
  action    String   // "CREATE", "UPDATE", "DELETE"
  resource  String   // "User", "Order", etc.
  resourceId String
  changes   Json?
  ipAddress String?
  createdAt DateTime @default(now())

  user      User     @relation(fields: [userId], references: [id])

  @@index([userId])
  @@index([resource, resourceId])
}
```

---

## Dependency Security

### GitHub Security Features

**Enable all GitHub security features:**

#### 1. Dependabot Alerts

- Settings → Security & analysis → Dependabot alerts (Enable)
- Automatically detects vulnerable dependencies
- Creates security advisories
- Provides upgrade recommendations

#### 2. Dependabot Security Updates

- Settings → Security & analysis → Dependabot security updates (Enable)
- Auto-creates PRs to fix vulnerable dependencies
- Review and merge promptly
- Configure in `.github/dependabot.yml`:

```yaml
version: 2
updates:
  # Enable version updates for npm
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'
    open-pull-requests-limit: 10
    groups:
      production-dependencies:
        patterns:
          - '*'
        update-types:
          - 'minor'
          - 'patch'
```

#### 3. Code Scanning (CodeQL)

- Settings → Security & analysis → Code scanning (Enable)
- Automatic vulnerability detection in code
- Scans for:
  - SQL injection
  - XSS vulnerabilities
  - Command injection
  - Path traversal
  - Hardcoded credentials
- Configure in `.github/workflows/codeql.yml`:

```yaml
name: 'CodeQL'

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1' # Weekly on Monday

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: ['javascript', 'typescript']

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
```

#### 4. Secret Scanning

- Settings → Security & analysis → Secret scanning (Enable)
- Automatically detects committed secrets:
  - API keys
  - Passwords
  - Private keys
  - Tokens
  - Connection strings
- Push protection (Enable): Prevents pushes containing secrets
- Receive alerts when secrets are detected

#### 5. Security Advisories

- Repository → Security → Advisories
- Private security reporting enabled
- Create private security advisories for vulnerabilities
- Coordinate fixes before public disclosure

### Manual Audits

**Run npm audit:**

```bash
# Check for vulnerabilities
pnpm audit

# Auto-fix (review changes)
pnpm audit --fix
```

### Minimal Dependencies

**Each dependency is a risk:**

- Review before adding
- Check maintenance status
- Check licenses
- Check download count / popularity
- Prefer well-maintained libraries

### Lock File Integrity

**Always commit lock files:**

- `pnpm-lock.yaml` must be committed
- Ensures reproducible builds
- Prevents supply chain attacks

---

## Security Checklist

### Pre-Deployment

- [ ] All routes require authentication (unless explicitly public)
- [ ] Authorization checks on all protected operations
- [ ] All inputs validated (Zod schemas)
- [ ] All outputs sanitized (XSS prevention)
- [ ] Secrets in Key Vault, not code
- [ ] HTTPS enforced
- [ ] Security headers configured (Helmet)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] SQL injection prevented (Prisma)
- [ ] Passwords hashed (bcrypt)
- [ ] PII encrypted
- [ ] Error messages don't leak info
- [ ] Dependencies scanned (no high/critical vulns)
- [ ] Audit logging enabled
- [ ] Session management secure
- [ ] File uploads validated
- [ ] CSP configured

### Code Review

- [ ] No hardcoded secrets
- [ ] No commented-out sensitive code
- [ ] Auth/authz checks present
- [ ] Input validation present
- [ ] Error handling doesn't expose internals
- [ ] Logging doesn't include PII

### Regular Tasks

**Weekly:**

- [ ] Review Dependabot PRs
- [ ] Check CodeQL scan results
- [ ] Review secret scanning alerts
- [ ] Check audit logs for anomalies

**Monthly:**

- [ ] Review security advisories
- [ ] Review access permissions
- [ ] Test backup restore
- [ ] Rotate non-user credentials
- [ ] Review GitHub security overview

**Quarterly:**

- [ ] Security audit
- [ ] Penetration testing (if applicable)
- [ ] Update security documentation
- [ ] Review and update security policies

---

## OWASP Top 10 Protection

### 1. Broken Access Control

- ✅ Authenticate all routes
- ✅ Verify permissions before actions
- ✅ Test authorization edge cases

### 2. Cryptographic Failures

- ✅ Use HTTPS everywhere
- ✅ Encrypt sensitive data
- ✅ Use strong algorithms (AES-256, bcrypt)

### 3. Injection

- ✅ Use Prisma (parameterized queries)
- ✅ Validate all inputs (Zod)
- ✅ Sanitize outputs

### 4. Insecure Design

- ✅ Security requirements from start
- ✅ Threat modeling
- ✅ Secure defaults

### 5. Security Misconfiguration

- ✅ Helmet for security headers
- ✅ Remove default accounts
- ✅ Error handling doesn't leak info

### 6. Vulnerable Components

- ✅ Dependabot enabled
- ✅ Regular updates
- ✅ Minimal dependencies

### 7. Authentication Failures

- ✅ Use Azure AD (MFA supported)
- ✅ Rate limit auth endpoints
- ✅ Secure session management

### 8. Software & Data Integrity

- ✅ Lock file committed
- ✅ Signed releases
- ✅ Audit logging

### 9. Logging Failures

- ✅ Log security events
- ✅ Don't log PII
- ✅ Monitor logs

### 10. Server-Side Request Forgery

- ✅ Validate URLs
- ✅ Whitelist allowed domains
- ✅ Use allow lists, not deny lists

---

## Incident Response

### If Security Issue Found

**1. Assess severity:**

- Critical: Immediate production risk
- High: Significant risk, needs quick fix
- Medium: Should fix soon
- Low: Fix in regular cycle

**2. Contain:**

- Can we disable the vulnerable feature?
- Hotfix needed?
- Notify users?

**3. Fix:**

- Create hotfix branch
- Minimal fix
- Test thoroughly
- Deploy immediately

**4. Post-mortem:**

- How did this happen?
- How do we prevent similar issues?
- Update security guidelines

**5. Notify (if required):**

- Affected users
- Regulatory bodies
- Public disclosure (responsible)

---

## Resources

**Internal:**

- [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md)
- [CODE_REVIEW_CHECKLIST.md](./CODE_REVIEW_CHECKLIST.md)

**External:**

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [Azure Security Best Practices](https://docs.microsoft.com/en-us/azure/security/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)

---

**Security is everyone's responsibility. When in doubt, ask!**

**Report security issues immediately to security team, not via public channels.**
