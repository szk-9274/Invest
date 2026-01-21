---
description: Review code for quality, security, and maintainability. Especially important for Electron security and React best practices.
---

# Code Review Command

This command invokes the **code-reviewer** agent for comprehensive code review.

## What This Command Does

1. Analyzes recent git changes
2. Checks for security issues (critical for Electron)
3. Reviews code quality and patterns
4. Validates TypeScript usage
5. Provides prioritized feedback

## When to Use

Use `/code-review` when:
- Before committing changes
- After implementing a feature
- Before creating a PR
- When refactoring code
- Reviewing someone else's code

## Review Categories

### Critical (Must Fix)
- Security vulnerabilities
- Electron security misconfigurations
- Hardcoded secrets

### High (Should Fix)
- Missing error handling
- Code quality issues
- Missing tests

### Medium (Consider)
- Performance optimizations
- React best practices
- TypeScript improvements

## Electron-Specific Checks

- contextIsolation enabled
- nodeIntegration disabled (or properly isolated)
- Secure IPC patterns
- No remote module usage
- Proper webPreferences
