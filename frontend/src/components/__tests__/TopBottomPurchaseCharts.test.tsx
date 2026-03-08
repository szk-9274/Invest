import { describe, it, expect, vi } from 'vitest'

// Mock plotly before importing the component module to avoid jsdom/canvas issues
vi.mock('react-plotly.js', () => ({
  default: () => <div data-testid="plotly-chart" />,
}))

import { calculateSymbolSize } from '../../components/TopBottomPurchaseCharts'

describe('calculateSymbolSize (unit tests)', () => {
  it('returns a minimum size for non-positive or invalid amounts', () => {
    expect(calculateSymbolSize(0)).toBeGreaterThan(0)
    expect(calculateSymbolSize(-10)).toBeGreaterThan(0)
    expect(calculateSymbolSize(Number.NaN)).toBeGreaterThan(0)
  })

  it('scales with sqrt', () => {
    const a = calculateSymbolSize(100)
    const b = calculateSymbolSize(400)
    expect(b).toBeGreaterThan(a)
  })
})
