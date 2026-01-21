---
description: Automatically diagnose and fix build errors in this Electron + Vite + TypeScript project.
---

# Build Fix Command

Diagnose and fix build errors automatically.

## What This Command Does

1. Run the build command
2. Parse error output
3. Identify root causes
4. Apply fixes
5. Verify build succeeds

## Build Commands for This Project

```bash
# Full build (TypeScript + Vite)
npm run build

# TypeScript only
npx tsc

# Vite renderer build
npm run renderer:build
```

## Common Build Errors

### TypeScript Errors
- Type mismatches
- Missing type definitions
- Import path issues

### Vite Errors
- Module resolution
- Asset handling
- Plugin configuration

### Electron-Builder Errors
- Missing icons
- Invalid configuration
- Path issues

## Usage

```
/build-fix
```

The command will:
1. Run `npm run build`
2. Capture and analyze errors
3. Fix issues automatically
4. Re-run build to verify
