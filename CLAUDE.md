# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

### Development (with hot reload)
```bash
npm run dev:hmr
```
Runs three processes concurrently: TypeScript watch (`tsc:watch`), Vite dev server (`renderer:dev`), and Electron with nodemon (`electron:dev`).

### Production preview
```bash
npm run start:prod
```
Builds and runs the app in production mode (no hot reload).

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

## Architecture

This is an Electron desktop application for Windows with a React frontend bundled by Vite.

### Directory Structure
- `src/` - Electron main process code (TypeScript, compiled to `dist/`)
  - `main.ts` - Main process entry, window management, IPC handlers
  - `preload.ts` - Context bridge exposing `window.win` and `window.gitlab` APIs
- `renderer/` - React frontend (TypeScript/TSX, bundled to `renderer-dist/`)
  - `src/App.tsx` - Main app component with navigation and page rendering
  - `src/components/` - Reusable UI components (Titlebar, Icons)
  - `src/types/` - TypeScript declarations for preload APIs

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
