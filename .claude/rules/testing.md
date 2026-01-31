# Testing Requirements
This document defines detailed testing practices.

If there is any conflict between this file and `.claude/rules.md`,
the root rules.md MUST take precedence.

## Minimum Test Coverage: 80%

Test Types (ALL required):
1. **Unit Tests** - Individual functions, utilities, React components
2. **Integration Tests** - IPC handlers, API interactions
3. **E2E Tests** - Critical user flows (Playwright + Electron)

## Test-Driven Development

MANDATORY workflow:
1. Write test first (RED)
2. Run test - it should FAIL
3. Write minimal implementation (GREEN)
4. Run test - it should PASS
5. Refactor (IMPROVE)
6. Verify coverage (80%+)

## Testing Stack Recommendations

### Unit/Integration Tests
- Vitest (Vite-native, fast)
- @testing-library/react
- @testing-library/jest-dom

### E2E Tests
- Playwright with @playwright/test
- electron-playwright for Electron-specific testing

## Test File Organization

```
src/
  main.ts
  main.test.ts           # Unit tests for main process

renderer/src/
  components/
    Button.tsx
    Button.test.tsx      # Component tests
  hooks/
    useData.ts
    useData.test.ts      # Hook tests

e2e/
  app.spec.ts            # E2E tests
```

## Troubleshooting Test Failures

1. Use **tdd-guide** agent
2. Check test isolation
3. Verify mocks are correct
4. Fix implementation, not tests (unless tests are wrong)

## Agent Support

- **tdd-guide** - Use PROACTIVELY for new features, enforces write-tests-first
