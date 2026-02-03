This document defines mandatory behaviors and constraints for Claude Code when working in this repository. 
These rules take precedence over any implicit assumptions or general expectations. 
Failure to follow these rules will be considered a task failure.

## Project Overview

This project is a Python-based stock screening and backtesting system designed as a data pipeline.

The system operates in clearly separated stages:

- Stage1: Build and normalize a broad stock universe from multiple sources.
- Stage2: Apply technical screening rules to generate trade candidates.
- Backtest: Simulate trade execution over a historical period using Stage2 results.

The primary interaction method is a CLI interface (`main.py --mode ...`).
There is no frontend or UI layer.

Each stage produces explicit outputs (CSV, logs, cache files) that are reused by downstream stages.
Stages must remain loosely coupled and executable independently.

This project prioritizes:
- Debuggability via structured logging
- Deterministic and reproducible runs
- Incremental execution and re-runs without recomputing completed stages

## Critical Rules

### Test-Driven Development (MANDATORY) ※Process Description

**Always write tests FIRST:**
1. Write failing test (RED)
2. Write minimal code to pass (GREEN)
3. Refactor (IMPROVE)
4. Verify 80%+ coverage

Use `/tdd` command to enforce this workflow.

### Testing　※Types of Tests

- TDD: Write tests first
- 80% minimum coverage
- Unit tests for utilities
- Integration tests for APIs
- E2E tests for critical flows

### Code Organization

- Many small files over few large files
- High cohesion, low coupling
- 200-400 lines typical, 800 max per file
- Organize by feature/domain, not by type

### Code Style

- No emojis in code, comments, or documentation
- No console.log in production code
- Proper error handling with try/catch

### 4. Security

- No hardcoded secrets
- Environment variables for sensitive data
- Validate all user inputs

## File Structure

- main.py  
  Entry point. Controls execution modes (stage2, backtest).
- python/stage2/  
  Stage 2 technical screening logic. Outputs screening_results.csv.
- python/backtest/  
  Backtest engine. Consumes Stage 2 output and simulates trades.
- python/scripts/  
  Standalone scripts (e.g. ticker universe update).
- python/config/  
  Configuration, thresholds, and constants.
- python/utils/  
  Shared helpers (logging, data loading, I/O).
- python/output/  
  Generated artifacts (screening results, backtest outputs).

### Role Discipline
Claude Code must explicitly switch roles as required. Before taking any action, it should clearly state which agent is currently active.

#### **planner**
* Task decomposition, scope clarification, and execution planning.

#### **tdd-guide**
* Writing or updating tests prior to, or in parallel with, implementation.
* **Mandatory** for data pipelines, scripts, and changes to logic involving side effects.

#### **code-reviewer**
* Identification of risks, assumptions, and constraints.
* Verification of the safety and maintainability of changes.

### Available Commands
* `/tdd` – Test-Driven Development workflow.
* `/plan` – Create an implementation plan.
* `/code-review` – Perform a code quality review.
* `/build-fix` – Resolve build errors.

## Git Workflow

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- Never commit to main directly
- PRs require review
- All tests must pass before merge

## python

### 3. Script-Specific Rules (python/scripts)
Files located under `python/scripts/` are treated as **executable entry points**.

When modifying these files:
* **Assume direct execution**: Design scripts to be invoked directly via CLI.
* **Validate CLI argument parsing**: Ensure parameters are correctly handled.
* **Guarantee crash-free startup**: Ensure scripts initialize without errors.
* **Prioritize smoke tests**: Focus on runtime execution checks over complex logic tests for scripts.
* **Fail fast and clearly**: Scripts must exit immediately with clear errors on invalid input.

### Future Roadmap (Non-binding): React + TypeScript 
Looking ahead, the project is intended to evolve into a full-stack desktop application.
* **`npm run dev:hmr`**: Dev mode (TS watch + Vite + Electron).
* **`npm run start:prod`**: Production mode preview.
* **`npm run build`**: Compile TS and build renderer to `renderer-dist/`.
* **`npm run dist`**: Generate NSIS installer in `release/`.
* **`npm run clean`**: Remove `dist/`, `renderer-dist/`, and `release/`.
* **`npm test`**: Run tests / **`npm run test:coverage`**: Run with coverage.