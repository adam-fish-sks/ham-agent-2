# Deployment Process

**Last Updated:** January 8, 2026  
**Status:** Active  
**Purpose:** Standard deployment procedures for all environments

---

## Table of Contents

1. [Environments](#environments)
2. [Deployment Pipeline](#deployment-pipeline)
3. [Pre-Deployment](#pre-deployment)
4. [Deployment Steps](#deployment-steps)
5. [Post-Deployment](#post-deployment)
6. [Rollback Procedures](#rollback-procedures)
7. [Database Migrations](#database-migrations)
8. [Feature Flags](#feature-flags)
9. [Monitoring](#monitoring)

---

## Environments

### Environment Strategy

We use three environments:

| Environment | Purpose | Auto-Deploy | URL |
|------------|---------|-------------|-----|
| **Development** | Local development | No | localhost |
| **Staging** | Pre-production testing | Yes (on merge to main) | staging.example.com |
| **Production** | Live users | Yes (on git tag) | app.example.com |

### Environment Configuration

**Development:**
- Local Docker Compose
- Local PostgreSQL, Redis
- Azure Storage Emulator (Azurite)
- `.env.local` for configuration

**Staging:**
- Azure Container Apps (minimal SKU)
- Azure PostgreSQL (Burstable tier)
- Azure Redis (Basic tier)
- Mirrors production architecture
- Test data only

**Production:**
- Azure Container Apps (scaled)
- Azure PostgreSQL (General Purpose)
- Azure Redis (Standard tier)
- Real user data
- High availability enabled

---

## Deployment Pipeline

### Continuous Integration (CI)

**Triggers:** Push, Pull Request

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      
      - run: pnpm install
      - run: pnpm turbo lint
      - run: pnpm turbo typecheck
      - run: pnpm turbo test
      - run: pnpm turbo build
```

**All checks must pass before merge.**

### Continuous Deployment (CD)

**Staging Deployment:**

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker images
        run: |
          docker build -t acr.azurecr.io/app-web:${{ github.sha }} ./apps/web
          docker build -t acr.azurecr.io/app-api:${{ github.sha }} ./apps/api
          docker build -t acr.azurecr.io/app-worker:${{ github.sha }} ./apps/worker
      
      - name: Push to ACR
        run: |
          echo ${{ secrets.ACR_PASSWORD }} | docker login acr.azurecr.io -u ${{ secrets.ACR_USERNAME }} --password-stdin
          docker push acr.azurecr.io/app-web:${{ github.sha }}
          docker push acr.azurecr.io/app-api:${{ github.sha }}
          docker push acr.azurecr.io/app-worker:${{ github.sha }}
      
      - name: Deploy to Azure
        uses: azure/CLI@v1
        with:
          azcliversion: latest
          inlineScript: |
            az containerapp update \
              --name app-web-staging \
              --resource-group rg-staging \
              --image acr.azurecr.io/app-web:${{ github.sha }}
```

**Production Deployment:**

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    # Similar to staging but targets production
    # Requires approval
    environment: production
    # ... deployment steps
```

---

## Pre-Deployment

### Pre-Deployment Checklist

**Before deploying to production:**

- [ ] All CI checks pass
- [ ] Code review approved
- [ ] Tested in staging
- [ ] Database migrations prepared
- [ ] Breaking changes documented
- [ ] Rollback plan ready
- [ ] Monitoring configured
- [ ] Feature flags configured
- [ ] Documentation updated
- [ ] Stakeholders notified (if major)

### Communication

**For major releases:**
1. Notify team 24 hours in advance
2. Post in team channel
3. Email stakeholders
4. Update status page (if downtime expected)

**Template:**
```
📦 Production Deployment Scheduled

Date: 2026-01-08 10:00 AM EST
Duration: ~30 minutes
Downtime: None expected

Changes:
- New user dashboard
- Performance improvements
- Bug fixes

Contact: @deploymentoneer for questions
```

---

## Deployment Steps

### Manual Deployment (if needed)

**1. Tag release:**

```bash
# Create and push tag
git tag -a v1.2.3 -m "Release 1.2.3"
git push origin v1.2.3
```

**2. Monitor deployment:**

```bash
# Watch GitHub Actions
# Visit: https://github.com/org/repo/actions

# Or watch Azure
az containerapp revision list \
  --name app-web-prod \
  --resource-group rg-prod
```

**3. Verify deployment:**

```bash
# Check health endpoint
curl https://app.example.com/api/health

# Check version
curl https://app.example.com/api/version
```

### Blue-Green Deployment

**For zero-downtime:**

```bash
# Deploy to "green" slot
az containerapp revision copy \
  --name app-web-prod \
  --resource-group rg-prod \
  --revision-suffix green-v1-2-3 \
  --image acr.azurecr.io/app-web:v1.2.3

# Test green deployment
curl https://app-web-prod--green-v1-2-3.example.com/api/health

# Switch traffic (gradual)
az containerapp ingress traffic set \
  --name app-web-prod \
  --resource-group rg-prod \
  --revision-weight green-v1-2-3=10 blue-v1-2-2=90

# Monitor metrics...

# Full cutover
az containerapp ingress traffic set \
  --name app-web-prod \
  --resource-group rg-prod \
  --revision-weight green-v1-2-3=100

# Decommission old
az containerapp revision deactivate \
  --name app-web-prod \
  --resource-group rg-prod \
  --revision blue-v1-2-2
```

---

## Post-Deployment

### Immediate Verification

**1. Health checks (within 1 minute):**

```bash
# API health
curl https://app.example.com/api/health
# Expected: 200 OK

# Web application
curl https://app.example.com
# Expected: 200 OK

# Worker (internal check)
# Check Application Insights for worker heartbeat
```

**2. Smoke tests (within 5 minutes):**

- [ ] Can users log in?
- [ ] Can users access dashboard?
- [ ] Can users perform key actions?
- [ ] Are background jobs running?

**3. Monitor metrics (within 15 minutes):**

- [ ] Error rate normal (<1%)
- [ ] Response times normal (<500ms p95)
- [ ] CPU/memory usage normal
- [ ] Database connections normal
- [ ] No spike in 500 errors

### Extended Monitoring

**Monitor for 1-2 hours after deployment:**

- Application Insights dashboard
- Error logs
- User feedback channels
- Performance metrics
- Background job queues

### Communication

**Post deployment:**
```
✅ Production Deployment Complete

Version: v1.2.3
Deployed: 2026-01-08 10:15 AM EST
Status: All systems operational

Metrics:
- Error rate: 0.2% (normal)
- Response time: 245ms p95 (improved)
- Deployment time: 12 minutes

Issues: None
```

---

## Rollback Procedures

### When to Rollback

**Immediate rollback if:**
- Critical functionality broken
- Security vulnerability introduced
- Data corruption detected
- Error rate >5%
- System unresponsive

### Rollback Steps

**1. Decision:**
- Incident commander decides
- Communicate decision to team
- Document reason

**2. Execute rollback:**

```bash
# Option 1: Revert to previous revision (fastest)
az containerapp revision set-mode \
  --name app-web-prod \
  --resource-group rg-prod \
  --mode single

az containerapp ingress traffic set \
  --name app-web-prod \
  --resource-group rg-prod \
  --revision-weight previous-revision=100

# Option 2: Redeploy previous tag
git push origin v1.2.2  # Previous known-good version
# CI/CD pipeline deploys automatically
```

**3. Rollback database migrations (if needed):**

```bash
# SSH to environment
# Run migration rollback
npx prisma migrate resolve --rolled-back <migration-name>
```

**4. Verify rollback:**
- Health checks pass
- Error rate drops
- Functionality restored

**5. Post-mortem:**
- What went wrong?
- How to prevent?
- Update tests/procedures

### Rollback Time Target

**Target:** < 5 minutes from decision to rollback complete

---

## Database Migrations

### Migration Strategy

**We use Prisma Migrate:**

```bash
# Create migration
npx prisma migrate dev --name add_user_role

# Deploy to production
npx prisma migrate deploy
```

### Migration Guidelines

**1. Migrations are forward-only:**
- No rollback capability
- Plan carefully
- Test thoroughly

**2. Breaking changes require multiple deploys:**

**Example: Renaming column**

```sql
-- Deploy 1: Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Deploy code to write to both columns

-- Deploy 2: Copy data
UPDATE users SET email_address = email WHERE email_address IS NULL;

-- Deploy code to read from new column only

-- Deploy 3: Drop old column
ALTER TABLE users DROP COLUMN email;
```

**3. Always add, never remove:**
- Add new columns (nullable or with default)
- Deprecate old columns
- Remove in later release

### Migration Deployment

**Automatic in CI/CD:**

```yaml
- name: Run Migrations
  run: npx prisma migrate deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

**Manual (emergency):**

```bash
# Connect to production database (via jump host)
DATABASE_URL="postgresql://..." npx prisma migrate deploy
```

### Migration Testing

**Test migrations in staging first:**

```bash
# Staging
DATABASE_URL=$STAGING_DB_URL npx prisma migrate deploy

# Verify data integrity
# Run smoke tests

# Then production
DATABASE_URL=$PROD_DB_URL npx prisma migrate deploy
```

---

## Feature Flags

### When to Use Feature Flags

**Use feature flags for:**
- Large features (phased rollout)
- Risky changes
- A/B testing
- Kill switches

### Implementation

**Simple flag system:**

```typescript
// Feature flags stored in database or config
const featureFlags = {
  newDashboard: false,
  darkMode: true,
  experimentalFeature: false,
};

export function isFeatureEnabled(flag: string): boolean {
  return featureFlags[flag] ?? false;
}

// Usage in code
if (isFeatureEnabled('newDashboard')) {
  return <NewDashboard />;
} else {
  return <OldDashboard />;
}
```

**Advanced: Percentage rollout**

```typescript
export function isFeatureEnabledForUser(
  flag: string,
  userId: string,
  percentage: number
): boolean {
  const hash = hashString(userId);
  return (hash % 100) < percentage;
}

// Enable for 10% of users
if (isFeatureEnabledForUser('newDashboard', user.id, 10)) {
  return <NewDashboard />;
}
```

### Feature Flag Lifecycle

1. **Development:** Flag off by default
2. **Staging:** Flag on for testing
3. **Production:** Gradual rollout (0% → 10% → 50% → 100%)
4. **Stable:** Remove flag, keep code
5. **Cleanup:** Remove old code path

**Don't let flags live forever** - remove after stable (2-4 weeks).

---

## Monitoring

### Application Insights

**Key metrics to monitor:**

```kusto
// Error rate
requests
| where timestamp > ago(1h)
| summarize 
    Total = count(),
    Errors = countif(success == false),
    ErrorRate = 100.0 * countif(success == false) / count()
| project ErrorRate

// Response time percentiles
requests
| where timestamp > ago(1h)
| summarize
    p50 = percentile(duration, 50),
    p95 = percentile(duration, 95),
    p99 = percentile(duration, 99)
```

### Alerts

**Configure alerts for:**

- Error rate >5% for 5 minutes
- Response time p95 >1000ms for 10 minutes
- Worker queue depth >1000 for 15 minutes
- Database CPU >80% for 10 minutes
- Failed deployments

**Alert channels:**
- Team Slack channel
- Email to on-call
- PagerDuty (critical only)

### Dashboards

**Create dashboards for:**
- Real-time metrics
- Deployment history
- Error tracking
- Performance trends
- Business metrics

---

## Deployment Schedule

### Regular Deployments

**Recommended schedule:**
- **Staging:** Multiple times daily (on merge)
- **Production:** 2-3 times per week
- **Hot fixes:** As needed

**Preferred times:**
- Weekdays, business hours
- Avoid Friday afternoons
- Avoid late nights
- Consider user timezone (minimal impact)

### Deployment Freeze

**Freeze periods (no deployments):**
- Major holidays
- Critical business periods
- Major events
- After major incidents (24-48 hours)

**Exceptions:**
- Security fixes (always allowed)
- Critical bug fixes (with approval)

---

## Troubleshooting Deployments

### Common Issues

**1. Deployment fails - health check timeout**
```bash
# Check logs
az containerapp logs show \
  --name app-web-prod \
  --resource-group rg-prod \
  --follow

# Check health endpoint
curl https://app.example.com/api/health -v
```

**2. Database migration fails**
```bash
# Check migration status
npx prisma migrate status

# Resolve failed migration
npx prisma migrate resolve --rolled-back <migration-name>

# Fix issue and re-run
npx prisma migrate deploy
```

**3. High error rate after deployment**
```bash
# Check Application Insights for errors
# Rollback immediately if critical

# Or hotfix if minor
```

**4. Slow deployment**
```bash
# Check image size
docker images | grep app-web

# Check resource limits
az containerapp show \
  --name app-web-prod \
  --resource-group rg-prod \
  --query "properties.template.containers[0].resources"
```

---

## Deployment Checklist Template

```markdown
## Deployment Checklist - v1.2.3

### Pre-Deployment
- [ ] CI checks pass
- [ ] Code review approved  
- [ ] Tested in staging
- [ ] Database migrations reviewed
- [ ] Breaking changes documented
- [ ] Rollback plan ready
- [ ] Team notified

### Deployment
- [ ] Tag created and pushed
- [ ] CI/CD pipeline triggered
- [ ] Database migrations run
- [ ] Health checks pass

### Post-Deployment
- [ ] Smoke tests pass
- [ ] Error rate normal
- [ ] Response times normal
- [ ] Monitoring shows green
- [ ] Team notified of completion

### Issues
- None

### Rollback
- Not needed
```

---

## Emergency Procedures

### On-Call Rotation

**On-call responsibilities:**
- Monitor alerts
- Respond to incidents
- Execute rollbacks
- Escalate if needed

**On-call schedule:**
- Weekly rotation
- Backup on-call available
- Escalation path defined

### Incident Response

**1. Alert received**
- Acknowledge alert
- Assess severity
- Notify team

**2. Investigate**
- Check logs
- Check metrics
- Identify root cause

**3. Mitigate**
- Rollback if needed
- Apply hotfix
- Monitor

**4. Post-mortem**
- Document incident
- Identify improvements
- Update runbooks

---

## Resources

- [Azure Container Apps docs](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Prisma Migrate docs](https://www.prisma.io/docs/concepts/components/prisma-migrate)
- [Application Insights docs](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)

---

**Safe deployments are automated, monitored, and reversible!**
