---
name: tdd-workflow
description: Test-Driven Development workflow for Electron + React + TypeScript projects.
---

# TDD Workflow

## The TDD Cycle

```
    +-------+
    |  RED  |  Write failing test
    +---+---+
        |
        v
    +-------+
    | GREEN |  Write minimal code to pass
    +---+---+
        |
        v
  +-----------+
  | REFACTOR  |  Improve code, keep tests passing
  +-----+-----+
        |
        +-------> Back to RED
```

## Step-by-Step Process

### 1. Define Interface First

```typescript
// Define what we need before writing any implementation
interface MetricResult {
  value: number
  timestamp: Date
  source: string
}

export function calculateMetric(input: number): MetricResult {
  throw new Error('Not implemented')
}
```

### 2. Write Failing Test (RED)

```typescript
describe('calculateMetric', () => {
  it('returns correct result for positive input', () => {
    const result = calculateMetric(100)

    expect(result.value).toBe(110)
    expect(result.source).toBe('calculation')
    expect(result.timestamp).toBeInstanceOf(Date)
  })

  it('throws for negative input', () => {
    expect(() => calculateMetric(-1)).toThrow('Input must be positive')
  })

  it('handles zero correctly', () => {
    const result = calculateMetric(0)
    expect(result.value).toBe(0)
  })
})
```

### 3. Run Test - Verify FAIL

```bash
npm test

# Expected output:
# FAIL  calculateMetric
#   x returns correct result for positive input
#     Error: Not implemented
```

### 4. Write Minimal Implementation (GREEN)

```typescript
export function calculateMetric(input: number): MetricResult {
  if (input < 0) {
    throw new Error('Input must be positive')
  }

  return {
    value: input * 1.1,
    timestamp: new Date(),
    source: 'calculation'
  }
}
```

### 5. Run Test - Verify PASS

```bash
npm test

# Expected output:
# PASS  calculateMetric
#   v returns correct result for positive input
#   v throws for negative input
#   v handles zero correctly
```

### 6. Refactor (IMPROVE)

```typescript
const MULTIPLIER = 1.1
const SOURCE = 'calculation'

export function calculateMetric(input: number): MetricResult {
  validateInput(input)

  return {
    value: input * MULTIPLIER,
    timestamp: new Date(),
    source: SOURCE
  }
}

function validateInput(input: number): void {
  if (input < 0) {
    throw new Error('Input must be positive')
  }
}
```

### 7. Verify Tests Still Pass

```bash
npm test
# All tests should still pass
```

## Testing React Components

### Component Test Example

```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  it('renders with label', () => {
    render(<Button label="Click me" onClick={() => {}} />)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Button label="Click" onClick={handleClick} />)

    fireEvent.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when loading', () => {
    render(<Button label="Submit" onClick={() => {}} loading />)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

## Testing IPC Handlers

### Mock Electron in Tests

```typescript
// __mocks__/electron.ts
export const ipcRenderer = {
  invoke: vi.fn(),
  send: vi.fn(),
  on: vi.fn(),
  removeListener: vi.fn()
}

// Test file
vi.mock('electron', () => ({
  ipcRenderer: {
    invoke: vi.fn()
  }
}))

describe('getData', () => {
  it('returns data from main process', async () => {
    const mockData = { id: '1', name: 'Test' }
    vi.mocked(ipcRenderer.invoke).mockResolvedValue(mockData)

    const result = await window.api.getData('1')

    expect(result).toEqual(mockData)
    expect(ipcRenderer.invoke).toHaveBeenCalledWith('get-data', '1')
  })
})
```

## Coverage Requirements

| Type | Minimum | Critical Code |
|------|---------|---------------|
| Statements | 80% | 100% |
| Branches | 80% | 100% |
| Functions | 80% | 100% |
| Lines | 80% | 100% |

Critical code includes:
- IPC handlers
- Security-related functions
- Core business logic
- Data validation
