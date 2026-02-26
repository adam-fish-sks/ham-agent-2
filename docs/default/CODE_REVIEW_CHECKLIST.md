# Code Review Checklist

**Last Updated:** January 8, 2026  
**Purpose:** Ensure consistent, thorough code reviews across all pull requests

---

## Quick Reference

Use this checklist when reviewing pull requests. Not every item applies to every PR - use judgment.

---

## Before Review

- [ ] CI/CD checks pass (build, lint, tests)
- [ ] PR has clear title and description
- [ ] PR is reasonably sized (< 500 lines ideal)
- [ ] Reviewers assigned

---

## 1. Functionality ⚙️

- [ ] **Code works as intended**
  - Logic is correct
  - Edge cases handled
  - No obvious bugs

- [ ] **Requirements met**
  - Solves the stated problem
  - Matches acceptance criteria
  - Related issue/ticket referenced

- [ ] **User experience**
  - Intuitive for end users
  - Error messages are helpful
  - Loading states handled

---

## 2. Code Quality 📝

### Readability

- [ ] **Code is self-explanatory**
  - Clear variable/function names
  - Logical structure
  - Not overly clever

- [ ] **Functions are focused**
  - Single responsibility
  - < 50 lines per function (guideline)
  - Reusable where appropriate

- [ ] **No code duplication**
  - DRY principle followed
  - Common logic extracted
  - Shared utilities used

### Standards Compliance

- [ ] **Follows naming conventions**
  - camelCase for variables/functions
  - PascalCase for components/classes
  - UPPER_SNAKE_CASE for constants
  - Boolean variables prefixed (is, has, should, can)

- [ ] **Follows project structure**
  - Files in correct directories
  - Imports organized properly
  - Barrel exports used

- [ ] **Style guidelines followed**
  - Prettier formatting applied
  - ESLint rules pass
  - No disabled rules without justification

---

## 3. TypeScript 🔷

- [ ] **Proper typing**
  - No `any` types (use `unknown` with guards)
  - Interfaces defined for props
  - Return types specified for exported functions
  - Type inference used appropriately

- [ ] **Type safety**
  - Strict null checks satisfied
  - No type assertions (`as`) without justification
  - Generic types used correctly

- [ ] **Imports organized**
  - Type imports last
  - Grouped logically (external, internal, relative)

---

## 4. React/Next.js ⚛️

### Component Structure

- [ ] **Server vs Client components**
  - `use client` only when needed
  - Server components for data fetching
  - Client components for interactivity

- [ ] **Props interface defined**
  - Not inline types
  - Clear prop names
  - Optional props marked with `?`

- [ ] **Hooks used correctly**
  - Rules of hooks followed
  - Dependencies arrays complete
  - No infinite loops

### Performance

- [ ] **Memoization appropriate**
  - `useMemo` for expensive calculations
  - `useCallback` for function props
  - `React.memo` for pure components
  - Not over-used (premature optimization)

- [ ] **Images optimized**
  - Using Next.js Image component
  - Appropriate sizes specified
  - Lazy loading considered

---

## 5. API/Backend 🔌

### Endpoints

- [ ] **REST conventions followed**
  - Appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE)
  - Resource-based URLs
  - Plural nouns

- [ ] **Request/response format**
  - JSON content-type
  - Consistent response envelope
  - Standard error format

- [ ] **Status codes correct**
  - 200/201/204 for success
  - 400/401/403/404 for client errors
  - 500/503 for server errors

### Data Handling

- [ ] **Input validation**
  - All inputs validated (use Zod)
  - SQL injection prevented (Prisma)
  - XSS prevented (sanitization)

- [ ] **Error handling**
  - Try-catch where needed
  - Errors logged properly
  - User-friendly error messages
  - Error types/codes used

- [ ] **Business logic in services**
  - Not in route handlers
  - Reusable service functions
  - Testable units

---

## 6. Database 🗄️

- [ ] **Prisma schema updated**
  - New models documented
  - Relationships defined
  - Indexes added for queries
  - Migrations generated

- [ ] **Queries optimized**
  - Select only needed fields
  - Avoid N+1 queries
  - Indexes used
  - Transactions for multi-step operations

- [ ] **Data integrity**
  - Constraints enforced
  - Validation before insert/update
  - Soft deletes considered

---

## 7. Testing 🧪

- [ ] **Tests included**
  - Unit tests for business logic
  - Integration tests for APIs
  - Component tests for UI (where critical)

- [ ] **Test coverage adequate**
  - Happy paths tested
  - Error cases tested
  - Edge cases tested
  - Coverage meets minimums (see TESTING_STRATEGY.md)

- [ ] **Tests are meaningful**
  - Actually test behavior, not implementation
  - Clear test names
  - Good assertions

- [ ] **Tests pass locally**
  - Reviewer runs tests
  - No flaky tests

---

## 8. Security 🔒

- [ ] **Authentication/authorization**
  - Protected routes have auth checks
  - User permissions verified
  - Tokens validated properly

- [ ] **Sensitive data**
  - No hardcoded secrets
  - Secrets use environment variables
  - Sensitive data not logged
  - PII handled properly

- [ ] **Input sanitization**
  - User input validated
  - HTML sanitized (DOMPurify)
  - File uploads validated

- [ ] **Dependencies**
  - No known vulnerabilities (Dependabot)
  - Unnecessary dependencies removed

---

## 9. Performance ⚡

- [ ] **No obvious bottlenecks**
  - Efficient algorithms
  - Pagination for large lists
  - Caching considered
  - Lazy loading where appropriate

- [ ] **Database queries efficient**
  - Indexes used
  - Minimal queries
  - Batch operations where possible

- [ ] **Bundle size considered**
  - Heavy dependencies justified
  - Code splitting where appropriate
  - Tree-shaking preserved

---

## 10. Accessibility ♿

- [ ] **Semantic HTML**
  - Proper heading hierarchy
  - Meaningful element choices
  - ARIA labels where needed

- [ ] **Keyboard navigation**
  - Focusable elements
  - Logical tab order
  - Keyboard shortcuts work

- [ ] **Screen reader friendly**
  - Alt text for images
  - Form labels present
  - Error messages announced

---

## 11. Documentation 📚

- [ ] **Code comments**
  - Complex logic explained
  - "Why" not "what" comments
  - JSDoc for exported functions
  - No commented-out code

- [ ] **Documentation updated**
  - README if setup changes
  - API docs if endpoints change
  - Architecture docs if needed

- [ ] **CHANGELOG updated**
  - Breaking changes noted
  - New features listed
  - Bug fixes mentioned

---

## 12. Infrastructure 🏗️

### Environment

- [ ] **Environment variables**
  - New vars documented
  - Example values in .env.example
  - Secrets in Key Vault

- [ ] **Configuration**
  - Feature flags used appropriately
  - Config changes backward compatible

### Deployment

- [ ] **Database migrations**
  - Migration scripts included
  - Rollback considered
  - Tested in dev/staging

- [ ] **Breaking changes**
  - Documented clearly
  - Migration path provided
  - Deprecation warnings added

- [ ] **Monitoring**
  - Logging added for important events
  - Metrics tracked
  - Alerts configured if critical

---

## 13. Dependencies 📦

- [ ] **Justified additions**
  - Dependency truly needed
  - No duplicate functionality
  - License compatible
  - Actively maintained

- [ ] **Version locked**
  - Exact versions in package.json
  - pnpm-lock.yaml updated

- [ ] **Bundle size impact**
  - Size increase acceptable
  - Tree-shakeable
  - Alternative lighter options considered

---

## Review Comments Guidelines

### Writing Comments

**Be constructive:**
```
✅ "Consider extracting this into a helper function for reusability"
❌ "This is bad"
```

**Be specific:**
```
✅ "This could cause a race condition if user clicks twice. Add debouncing."
❌ "Fix this"
```

**Use prefixes:**
- `MUST:` - Blocking, must fix
- `SHOULD:` - Strong suggestion
- `COULD:` - Nice to have
- `QUESTION:` - Need clarification
- `NITPICK:` - Minor preference
- `PRAISE:` - Positive feedback

### Approval Guidelines

**Approve when:**
- All MUST items resolved
- Functionality works
- Tests pass
- No major concerns

**Request changes when:**
- MUST items unresolved
- Functionality broken
- Tests failing
- Security issues
- Breaking standards

**Comment (no approval) when:**
- Minor suggestions only
- Questions for clarification
- Waiting on discussion

---

## Review Response Time

- **Initial response:** 4 hours
- **Full review:** 1 business day
- **Urgent PRs:** Same day (label as "urgent")

---

## Post-Review

### Author Responsibilities

- [ ] Address all MUST comments
- [ ] Respond to questions
- [ ] Consider SHOULD suggestions
- [ ] Re-request review when ready
- [ ] Resolve conversations once addressed

### Reviewer Responsibilities

- [ ] Re-review within 4 hours
- [ ] Verify fixes
- [ ] Approve if satisfied
- [ ] Mark conversations resolved

---

## Special Cases

### Documentation-Only PRs

Simplified review:
- [ ] Accuracy
- [ ] Clarity
- [ ] Formatting
- [ ] Links work

Can approve without full checklist.

### Dependency Updates

Automated PRs (Dependabot):
- [ ] CI passes
- [ ] No breaking changes in CHANGELOG
- [ ] Version bump appropriate

Can auto-merge if CI green.

### Hot Fixes

Expedited review:
- [ ] Fixes critical issue
- [ ] Minimal changes
- [ ] Tests included
- [ ] Deploy immediately after merge

---

## When to Involve Others

**Seek additional review for:**
- Security-sensitive changes
- Breaking changes
- Architecture changes
- Performance-critical code
- Complex algorithms
- Unfamiliar territory

**Tag specialists:**
- Security: `@security-team`
- Performance: `@performance-team`
- Accessibility: `@a11y-team`
- DevOps: `@devops-team`

---

## Tools

### Automated Checks

These run automatically in CI:
- Prettier formatting
- ESLint linting
- TypeScript compilation
- Unit tests
- Build success

If these fail, **fix before requesting human review**.

### Manual Testing

Test locally:
```bash
# Pull PR branch
gh pr checkout 123

# Install and build
pnpm install
pnpm build

# Run application
pnpm dev

# Test the feature manually
```

---

## Review Fatigue

**For large PRs:**
- Review in multiple sessions
- Focus on high-risk areas first
- Request PR be split if too large
- Don't rubber-stamp

**For reviewers:**
- Limit to 2-3 reviews per session
- Take breaks between reviews
- Don't review when tired
- It's okay to pass to another reviewer

---

## Summary

**Good code reviews:**
- ✅ Catch bugs before production
- ✅ Share knowledge
- ✅ Maintain standards
- ✅ Improve code quality
- ✅ Mentor developers

**Remember:**
- Be kind and constructive
- Focus on code, not person
- Explain reasoning
- Praise good work
- Learn from each other

---

**Questions about this checklist? Improve it via PR!**
