# Git Workflow

## Commit Format

Use Conventional Commits:

```
type(scope): description

feat:     New feature
fix:      Bug fix
refactor: Code change that neither fixes nor adds
docs:     Documentation only
test:     Adding or updating tests
chore:    Maintenance tasks
```

Examples:
```bash
git commit -m "feat(ipc): add system tray support"
git commit -m "fix(renderer): resolve memory leak in useData hook"
git commit -m "test(main): add unit tests for windowManager"
```

## Branch Strategy

- `main` - Production-ready code
- `feature/*` - New features
- `fix/*` - Bug fixes
- `refactor/*` - Code improvements

## PR Process

1. Create feature branch from main
2. Implement with TDD (tests first)
3. Run `/code-review` before PR
4. All tests must pass
5. Squash merge to main

## Pre-Commit Checklist

- [ ] All tests passing
- [ ] No console.log statements
- [ ] No hardcoded secrets
- [ ] Code reviewed with `/code-review`
- [ ] Build succeeds (`npm run build`)
- [ ] Commit message follows convention

## Never Commit

- `.env` files with secrets
- `node_modules/`
- Build artifacts (`dist/`, `renderer-dist/`, `release/`)
- IDE settings (unless shared)
