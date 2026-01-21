# Coding Style

## Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate:

```typescript
// WRONG: Mutation
function updateState(state, value) {
  state.value = value  // MUTATION!
  return state
}

// CORRECT: Immutability
function updateState(state, value) {
  return {
    ...state,
    value
  }
}
```

## File Organization

MANY SMALL FILES > FEW LARGE FILES:
- High cohesion, low coupling
- 200-400 lines typical, 800 max
- Extract utilities from large components
- Organize by feature/domain, not by type

### Project Structure
```
src/               # Main process
  main.ts          # Entry point
  preload.ts       # Context bridge
  utils/           # Main process utilities

renderer/src/      # React frontend
  App.tsx          # Main component
  components/      # UI components
  hooks/           # Custom hooks
  types/           # TypeScript types
```

## Error Handling

ALWAYS handle errors comprehensively:

```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  // Return graceful fallback or rethrow with context
  throw new Error('Operation failed: ' + error.message)
}
```

## TypeScript

- Avoid `any` - use `unknown` if type is uncertain
- Define interfaces for all data structures
- Use strict mode
- Export types from dedicated files

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable and well-named
- [ ] Functions are small (<50 lines)
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels)
- [ ] Proper error handling
- [ ] No console.log statements in production
- [ ] No hardcoded values
- [ ] No mutation (immutable patterns used)
