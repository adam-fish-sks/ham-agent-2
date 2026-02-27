# Contributing to HAM Agent

Thank you for contributing! Please follow these guidelines.

## Development Workflow

### 1. Branch Naming

Follow the convention: `{type}/{ticket-id}-{brief-description}`

Types:

- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation
- `test/` - Tests
- `chore/` - Dependencies, tooling

Example: `feature/DEV-123-user-authentication`

### 2. Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

Examples:

```
feat(api): add user authentication endpoint
fix(web): correct email validation regex
docs: update API design guidelines
```

### 3. Before Committing

Ensure all checks pass:

```bash
pnpm lint          # Lint code
pnpm typecheck     # Type check
pnpm test          # Run tests
pnpm format:check  # Check formatting
```

### 4. Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all CI checks pass
5. Request review from team members
6. Address review feedback
7. Squash and merge after approval

### 5. PR Title and Description

- Title: Follow commit message format
- Description: Use the PR template
- Link related issues

### 6. Code Review

Reviewers will check:

- Code quality and standards compliance
- Test coverage
- Documentation updates
- Security considerations

### 7. After Merge

- Delete your branch
- Pull latest `main`
- Start next feature

## Development Setup

See [GETTING_STARTED.md](./GETTING_STARTED.md) for setup instructions.

## Questions?

Ask in team chat or open a discussion issue.
