---
description: Create a detailed implementation plan for features, refactoring, or architectural changes in this Electron + React project.
---

# Plan Command

This command invokes the **planner** agent to create comprehensive implementation plans.

## What This Command Does

1. Analyze the feature request or change
2. Review existing codebase architecture
3. Break down into manageable steps
4. Identify dependencies and risks
5. Output a detailed implementation plan

## When to Use

Use `/plan` when:
- Starting a new feature
- Making architectural changes
- Planning a refactor
- Complex bug fixes
- Before major code changes

## Plan Output Format

The planner will produce:
- Overview of changes needed
- Architecture impact (main process, renderer, preload)
- Step-by-step implementation guide
- Testing strategy
- Risk assessment

## Example Usage

```
/plan Add system tray icon with context menu
```

Output will include:
- Changes to main.ts for tray creation
- IPC handlers needed
- Renderer UI components
- Test plan for tray functionality
