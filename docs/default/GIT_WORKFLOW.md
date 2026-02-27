# Git Workflow

**Last Updated:** January 8, 2026  
**Status:** Active  
**Purpose:** Define standardized version control practices for team collaboration

---

## Table of Contents

1. [Branching Strategy](#branching-strategy)
2. [Branch Naming](#branch-naming)
3. [Commit Messages](#commit-messages)
4. [Pull Request Process](#pull-request-process)
5. [Code Review](#code-review)
6. [Merging](#merging)
7. [Release Process](#release-process)
8. [Hot Fixes](#hot-fixes)
9. [Git Commands](#git-commands)

---

## Branching Strategy

We use a **simplified trunk-based development** workflow with short-lived feature branches.

### Main Branches

**`main`** - Production-ready code

- Always deployable
- Protected branch (requires PR + review)
- Automatically deploys to production
- Never commit directly to main

**`develop`** (optional) - Integration branch

- Use only if you need a staging environment
- Merges to main trigger production deploys
- We recommend **not using develop** - prefer trunk-based

### Feature Branches

**Short-lived branches** for all changes:

- Branch from `main`
- Merge back to `main` via PR
- Delete after merge
- Keep small (< 500 lines changed)
- Keep short-lived (< 3 days)

### Branch Diagram

```
main ─────────────●─────────●────────→
        \         /         /
         feature-1         /
                          /
                  feature-2
```

---

## Branch Naming

### Convention

```
{type}/{ticket-id}-{brief-description}
```

### Types

- `feature/` - New feature
- `fix/` - Bug fix
- `hotfix/` - Urgent production fix
- `refactor/` - Code refactoring
- `docs/` - Documentation only
- `test/` - Test additions/fixes
- `chore/` - Build, dependencies, tooling

### Examples

```bash
✅ Good
feature/DEV-123-user-authentication
fix/DEV-456-email-validation
hotfix/prod-payment-error
refactor/database-queries
docs/api-guidelines
chore/upgrade-dependencies

❌ Bad
my-feature
fix-bug
johns-branch
update
```

### Without Ticket IDs

If no ticket system:

```bash
feature/user-authentication
fix/email-validation
refactor/database-queries
```

---

## Commit Messages

### Format (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Formatting (no code change)
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `test:` - Adding/updating tests
- `chore:` - Build process, dependencies
- `ci:` - CI/CD changes
- `revert:` - Revert previous commit

### Scope (Optional)

Package or area affected:

```
feat(api): add user endpoint
fix(web): correct form validation
docs(readme): update setup instructions
chore(deps): upgrade prisma to 5.7
```

### Subject

- Use imperative mood ("add", not "added" or "adds")
- Don't capitalize first letter
- No period at the end
- Max 72 characters

### Examples

```bash
✅ Good
feat(api): add user authentication endpoint
fix(web): correct email validation regex
docs: update API design guidelines
refactor(database): optimize user queries
test(api): add auth endpoint tests
chore(deps): upgrade next.js to 14.2.35

❌ Bad
Added new feature
Fixed bug
WIP
updated
.
```

### Multi-line Commits

For complex changes:

```
feat(api): add user authentication endpoint

- Implement JWT token generation
- Add password hashing with bcrypt
- Create authentication middleware
- Add rate limiting to auth endpoints

Closes #123
```

### Breaking Changes

```
feat(api)!: change user response format

BREAKING CHANGE: User API now returns nested profile object
instead of flat structure.

Before: { id, name, email }
After: { id, profile: { name, email } }
```

---

## Pull Request Process

### 1. Before Creating PR

```bash
# Ensure branch is up to date
git checkout main
git pull origin main
git checkout feature/your-branch
git rebase main  # or merge main

# Run checks locally
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

### 2. Create PR

**Title:** Same as commit message format

```
feat(api): add user authentication endpoint
```

**Description Template:**

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass locally
- [ ] Dependent changes merged

## Related Issues

Closes #123
Relates to #456

## Screenshots (if applicable)

[Add screenshots]

## Additional Notes

Any additional context.
```

### 3. PR Size Guidelines

**Keep PRs small:**

- **Ideal:** < 200 lines changed
- **Max:** < 500 lines changed
- **If larger:** Break into multiple PRs

**Why:**

- Faster reviews
- Fewer bugs
- Easier to revert
- Better feedback

### 4. Draft PRs

Use draft PRs for:

- Work in progress
- Early feedback
- Showing approach

```
[WIP] feat(api): user authentication
```

Convert to ready when complete.

---

## Code Review

### Reviewer Responsibilities

**Review for:**

1. **Correctness** - Does it work? Any bugs?
2. **Design** - Is the approach sound?
3. **Readability** - Easy to understand?
4. **Tests** - Adequate test coverage?
5. **Documentation** - Comments/docs updated?
6. **Standards** - Follows guidelines?
7. **Security** - Any vulnerabilities?
8. **Performance** - Any issues?

### Review Timeline

- **Respond:** Within 4 hours
- **Complete:** Within 1 business day
- **Urgent:** Label as "urgent" for same-day review

### Review Comments

**Be constructive and specific:**

```
✅ Good
"Consider extracting this logic into a separate function for
reusability and testing. Something like `calculateDiscount(price, rate)`"

❌ Bad
"This is wrong"
"Bad code"
"Why did you do this?"
```

**Use conventional comment prefixes:**

- `MUST:` - Blocking issue, must be fixed
- `SHOULD:` - Strong suggestion, should be addressed
- `COULD:` - Nice to have, optional
- `QUESTION:` - Need clarification
- `NITPICK:` - Minor style preference
- `PRAISE:` - Positive feedback

**Examples:**

```
MUST: This has a SQL injection vulnerability. Use parameterized queries.

SHOULD: Extract this into a helper function for better testability.

COULD: Consider using a more descriptive variable name like `userCount`.

QUESTION: What happens if the user array is empty?

NITPICK: Extra space here (auto-fixed by Prettier anyway)

PRAISE: Great test coverage! Love the edge case handling.
```

### Approval Process

**Required approvals:**

- **1 approval** minimum
- **2 approvals** for critical changes (security, breaking changes)

**Auto-approve (no review needed):**

- Documentation-only changes
- Dependency updates (if CI passes)
- Auto-generated code

---

## Merging

### Merge Strategy

**Squash and Merge (Recommended)**

Benefits:

- Clean, linear history
- One commit per PR
- Easy to revert
- Bisect-friendly

```bash
# GitHub will squash all commits into one
# Edit commit message to be meaningful
```

**Alternative: Rebase and Merge**

Use when:

- Preserving commit history is important
- Commits are already well-crafted

```bash
# Maintains individual commits
# Linear history (no merge commits)
```

**Never: Merge Commit**

Avoid merge commits in our workflow.

### After Merge

1. **Delete branch** (automatic in GitHub)
2. **Pull latest main** locally
3. **Delete local branch**

```bash
git checkout main
git pull origin main
git branch -d feature/your-branch
```

---

## Release Process

### Version Numbering (Semantic Versioning)

```
MAJOR.MINOR.PATCH
Example: 1.2.3
```

- **MAJOR:** Breaking changes (1.x.x → 2.0.0)
- **MINOR:** New features (1.2.x → 1.3.0)
- **PATCH:** Bug fixes (1.2.3 → 1.2.4)

### Creating a Release

**1. Update version in package.json**

```bash
# Automatic with npm version
npm version patch  # 1.2.3 → 1.2.4
npm version minor  # 1.2.3 → 1.3.0
npm version major  # 1.2.3 → 2.0.0
```

**2. Create git tag**

```bash
git tag -a v1.2.4 -m "Release 1.2.4"
git push origin v1.2.4
```

**3. Create GitHub Release**

- Go to GitHub Releases
- Create new release from tag
- Add release notes (see template below)

**Release Notes Template:**

```markdown
## 🚀 Features

- Add user authentication (#123)
- Add dark mode support (#125)

## 🐛 Bug Fixes

- Fix email validation (#124)
- Correct timezone handling (#126)

## 🔧 Improvements

- Improve page load performance (#127)
- Update dependencies (#128)

## 📚 Documentation

- Update API documentation (#129)

## ⚠️ Breaking Changes

- Change user API response format (#130)

## 🙏 Contributors

Thanks to @user1, @user2 for contributions!
```

### Deployment

**Automatic deployment on tag push:**

```bash
# CI/CD pipeline triggers on tag push
git push origin v1.2.4

# Pipeline runs:
# 1. Build all apps
# 2. Run tests
# 3. Build Docker images
# 4. Deploy to production
```

---

## Hot Fixes

### For Critical Production Bugs

**1. Create hotfix branch from main**

```bash
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-description
```

**2. Make minimal fix**

- Only fix the critical issue
- No refactoring or additional features
- Add test to prevent regression

**3. Create PR with "HOTFIX" label**

```
hotfix: fix critical payment processing error

URGENT: Payment processing fails for orders > $1000

- Add validation for large transactions
- Add test case
- Add monitoring alert

Closes #999
```

**4. Fast-track review**

- Notify team immediately
- Get immediate review
- Merge ASAP

**5. Deploy immediately**

```bash
# Deploy hotfix to production
git tag -a v1.2.5 -m "Hotfix: payment processing"
git push origin v1.2.5
```

**6. Backport fix**

Ensure fix is in all active branches if needed.

---

## Git Commands

### Daily Workflow

```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/new-feature

# Keep branch updated
git checkout main
git pull origin main
git checkout feature/new-feature
git rebase main

# After PR is merged
git checkout main
git pull origin main
git branch -d feature/new-feature
```

### Useful Commands

```bash
# View branch history
git log --oneline --graph --all

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Amend last commit message
git commit --amend

# Stash changes temporarily
git stash
git stash pop

# View changes
git diff
git diff --staged

# Clean up merged branches
git branch --merged | grep -v main | xargs git branch -d

# Force push after rebase (use with caution)
git push --force-with-lease
```

### Interactive Rebase

Clean up commits before PR:

```bash
# Rebase last 3 commits
git rebase -i HEAD~3

# In editor:
pick abc123 feat: add feature
squash def456 fix typo
squash ghi789 fix lint

# Results in single commit
```

---

## Git Configuration

### Setup

```bash
# Set name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch
git config --global init.defaultBranch main

# Set default editor
git config --global core.editor "code --wait"

# Enable colors
git config --global color.ui true

# Set pull strategy
git config --global pull.rebase false

# Set up aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all"
```

### .gitignore

Essential entries:

```gitignore
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
dist/
build/
.next/

# Environment
.env
.env.local
.env*.local

# IDE
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*

# Database
*.db
*.sqlite

# Prisma
.prisma/client/
migrations/.migrations_lock

# Misc
.turbo/
.cache/
```

---

## Troubleshooting

### Merge Conflicts

```bash
# During rebase or merge
# 1. Open conflicted files
# 2. Resolve conflicts (keep both, choose one, or edit)
# 3. Mark as resolved
git add .
git rebase --continue  # or git merge --continue

# Abort if needed
git rebase --abort
git merge --abort
```

### Accidentally Committed to Main

```bash
# Reset main to match remote
git checkout main
git reset --hard origin/main

# Create feature branch with your changes
git checkout -b feature/your-feature
git cherry-pick <commit-hash>
```

### Lost Commits

```bash
# Find lost commits
git reflog

# Recover commit
git checkout <commit-hash>
git checkout -b recovered-branch
```

---

## Best Practices

### Do's ✅

- Commit early, commit often
- Write descriptive commit messages
- Keep PRs small and focused
- Review your own PR before requesting review
- Pull/rebase frequently
- Delete merged branches
- Tag releases consistently
- Use .gitignore properly

### Don'ts ❌

- Don't commit sensitive data (keys, passwords)
- Don't commit dependencies (node_modules)
- Don't commit generated files (.next, dist)
- Don't force push to main
- Don't commit commented-out code
- Don't use vague commit messages ("fix", "update")
- Don't let branches live too long
- Don't commit large binary files

---

## Questions?

If anything is unclear:

1. Ask in team chat
2. Check GitHub documentation
3. Propose changes to this document via PR

---

**This workflow is designed to enable fast, safe, collaborative development!**
