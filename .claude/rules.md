# Claude Code Project Rules (Invest)

This document defines mandatory behavior and constraints for Claude Code
when working on this repository.

These rules override any implicit assumptions.
Failure to follow these rules is considered a task failure.

---

## 1. Core Philosophy

- This project prioritizes **correct execution over elegant code**
- Static reasoning alone is insufficient
- Any change must preserve the ability to **run without crashing**
- Silent runtime failures are unacceptable

Claude Code must behave as a cautious engineer, not just a code generator.

---

## 2. Mandatory Execution Rule (NON-NEGOTIABLE)

After modifying **any Python code**, Claude Code MUST:

- Execute at least **one minimal runtime command**
- Confirm that the code starts successfully

Examples of acceptable execution checks:

- `python main.py --help`
- `python main.py --mode stage2 --help`
- `python scripts/update_tickers_extended.py --help`
- `pytest tests/smoke`

If execution is not possible, Claude Code MUST:
- Explicitly state why
- Propose an alternative minimal validation

❌ Static analysis alone is NOT sufficient  
❌ “Looks correct” is NOT acceptable

---

## 3. Script-Level Rules (`python/scripts`)

Files under `python/scripts/` are treated as **executable entry points**.

When modifying these files:

- Assume they will be run directly
- Validate CLI argument parsing
- Ensure the script starts without crashing
- Prefer runtime smoke tests over logic-heavy tests

Scripts must fail fast and clearly if inputs are invalid.

---

## 4. Pandas / CSV Safety Rules (CRITICAL)

Pandas-related bugs are considered high-risk.

When modifying code that:
- Reads CSV
- Writes CSV
- Selects DataFrame columns

Claude Code MUST:

- Explicitly verify that required columns exist
- Never assume column presence implicitly
- Avoid silent `df[columns]` without validation

If columns are optional:
- Handle missing columns explicitly
- Or document the requirement clearly

The following class of errors MUST be prevented:
- `KeyError: None of [Index(...)] are in the [columns]`

---

## 5. Testing Expectations (Minimal but Mandatory)

This project does NOT require high test coverage.

However, for any behavior change, Claude Code MUST:

- Add or update **at least one minimal test**
- Prefer smoke / contract tests over full logic tests

Valid test goals include:
- Script can start
- CLI arguments are accepted
- Required outputs / columns exist
- No crash on minimal input

Small tests are preferred over untested assumptions.

---

## 6. Backtest / Screening Design Constraints

- Zero trades is a valid and expected outcome
- Absence of trades is NOT a bug by default
- Minervini-style strictness must be preserved

Claude Code MUST NOT loosen screening or RS conditions
unless explicitly instructed.

---

## 7. Logging and Warnings Policy

- Suppressing third-party warnings is allowed ONLY if:
  - The warning is non-actionable
  - The behavior is documented

- Runtime errors MUST NOT be silenced
- Important warnings MUST remain visible

---

## 8. Role Discipline

Claude Code MUST explicitly switch roles when appropriate:

- Engineer: implement changes
- Tester: validate execution
- Reviewer: explain risks and limitations

If multiple roles are required, Claude Code should state them clearly.

### Agent Discipline (Non-trivial Changes)

For non-trivial changes, Claude Code SHOULD explicitly switch agents
to guide its behavior and reasoning process.

The following agents SHOULD be used where appropriate:

- planner  
  - For task decomposition, scope clarification, and execution planning

- tdd-guide  
  - For writing or updating tests before or alongside implementation
  - Especially when modifying data pipelines, scripts, or logic with side effects

- code-reviewer  
  - For identifying risks, assumptions, and limitations
  - For validating that changes are safe and maintainable

Claude Code SHOULD clearly state which agent is active before acting.

---

## 9. Completion Requirements

A task is considered complete ONLY if:

- Code changes are implemented
- Minimal execution has been validated
- Any limitations or assumptions are documented
- A merge-ready state is confirmed

If any requirement cannot be met, Claude Code MUST say so explicitly.
