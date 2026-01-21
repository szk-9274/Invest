# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Electron + React + TypeScript desktop application for Windows, bundled with Vite.

## Critical Rules

### 1. Test-Driven Development (MANDATORY)

**Always write tests FIRST:**
1. Write failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor (IMPROVE)
4. Verify 80%+ coverage

Use `/tdd` command to enforce this workflow.

### 2. Code Organization

- Many small files over few large files
- 200-400 lines typical, 800 max per file
- Organize by feature/domain
- High cohesion, low coupling

### 3. Security (Electron-Critical)

- contextIsolation: true (ALWAYS)
- nodeIntegration: false (ALWAYS)
- No hardcoded secrets
- Validate all IPC inputs
- Use environment variables for sensitive data

### 4. Code Style

- Immutability always - never mutate objects or arrays
- No console.log in production code
- Proper error handling with try/catch
- TypeScript strict mode

## Build and Development Commands

### Development (with hot reload)
```bash
npm run dev:hmr
```
Runs three processes concurrently: TypeScript watch, Vite dev server, Electron with nodemon.

### Production preview
```bash
npm run start:prod
```
Builds and runs the app in production mode.

### Build only
```bash
npm run build
```
Compiles TypeScript and builds the Vite renderer to `renderer-dist/`.

### Create Windows installer
```bash
npm run dist
```
Builds and creates NSIS installer in `release/`.

### Clean build artifacts
```bash
npm run clean
```
Removes `dist/`, `renderer-dist/`, and `release/` directories.

### Testing (when configured)
```bash
npm test              # Run tests
npm run test:coverage # Run with coverage
```

## Architecture

### Directory Structure
```
src/                    # Electron main process
  main.ts               # Entry, window management, IPC handlers
  preload.ts            # Context bridge (window.win, window.gitlab)

renderer/               # React frontend
  src/
    App.tsx             # Main component
    components/         # UI components
    hooks/              # Custom hooks
    types/              # TypeScript declarations

.claude/                # Claude Code configuration
  agents/               # Specialized subagents
  commands/             # Slash commands
  rules/                # Always-follow guidelines
  skills/               # Workflow definitions
```

### IPC Communication
- Main process handles: `win:minimize`, `win:close`, `gitlab:openProjectWeb`
- Preload exposes: `window.win.minimize()`, `window.win.close()`, `window.gitlab.openProjectWeb()`

### TypeScript Configuration
- Root `tsconfig.json` - Main/preload process (CommonJS, outputs to `dist/`)
- `renderer/tsconfig.json` - React frontend (noEmit, Vite handles bundling)

### Dev vs Production Mode
Controlled by `USE_DEV_SERVER` environment variable:
- `true`: Loads from Vite dev server (http://127.0.0.1:5173), auto-opens DevTools
- `false`: Loads built static files from `renderer-dist/`

## Available Commands

- `/tdd` - Test-driven development workflow
- `/plan` - Create implementation plan
- `/code-review` - Review code quality
- `/build-fix` - Fix build errors

## Git Workflow

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- All tests must pass before commit
- Use `/code-review` before PR
