import { act, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { BacktestAnalysisPage } from './BacktestAnalysisPage'

const { contextMock, chartsMock } = vi.hoisted(() => ({
  contextMock: vi.fn(),
  chartsMock: vi.fn((_props: { trades: unknown[] }) => <div data-testid="charts-view">chart gallery</div>),
}))

const observerInstances: Array<{ callback: IntersectionObserverCallback }> = []

vi.mock('./BacktestDashboard', () => ({
  useBacktestDashboardContext: () => contextMock(),
}))

vi.mock('../components/BacktestSummary', () => ({
  BacktestSummary: ({ data }: { data: { total_trades?: number } }) => (
    <div data-testid="summary-view">summary:{data.total_trades ?? 0}</div>
  ),
}))

vi.mock('../components/TradeTable', () => ({
  TradeTable: ({ trades }: { trades: unknown[] }) => <div data-testid="trades-view">trades:{trades.length}</div>,
}))

vi.mock('../components/TopBottomPurchaseCharts', () => ({
  TopBottomPurchaseCharts: (props: { trades: unknown[] }) => chartsMock(props),
}))

const sampleResults = {
  timestamp: 'backtest_2025-01-01_to_2025-12-31_20251231-235959',
  summary: { total_trades: 2 },
  trades: [{ ticker: 'AAA' }, { ticker: 'BBB' }],
  ticker_stats: [{ ticker: 'AAA', total_pnl: 10, trade_count: 1 }],
  charts: {},
  run_metadata: {
    run_id: 'backtest_2025-01-01_to_2025-12-31_20251231-235959',
    run_label: 'baseline-run',
    experiment_name: 'qlib-inspired',
    strategy_name: 'rule-based-stage2',
    rule_profile: 'strict-auto-fallback',
    benchmark_enabled: false,
    tags: ['baseline'],
  },
}

describe('BacktestAnalysisPage', () => {
  beforeEach(() => {
    chartsMock.mockClear()
    contextMock.mockReturnValue({
      results: sampleResults,
      loading: false,
    })

    observerInstances.length = 0
    class MockIntersectionObserver {
      callback: IntersectionObserverCallback
      constructor(callback: IntersectionObserverCallback) {
        this.callback = callback
        observerInstances.push({ callback })
      }
      observe() {}
      disconnect() {}
      unobserve() {}
      takeRecords() { return [] }
      root = null
      rootMargin = '0px'
      thresholds = []
    }

    vi.stubGlobal('IntersectionObserver', MockIntersectionObserver)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders summary and trades immediately but defers charts until visible', async () => {
    render(<BacktestAnalysisPage />)

    expect(screen.getByTestId('summary-view')).toHaveTextContent('summary:2')
    expect(screen.getByTestId('trades-view')).toHaveTextContent('trades:2')
    expect(screen.getByText('baseline-run')).toBeInTheDocument()
    expect(screen.getByText('qlib-inspired / rule-based-stage2 / strict-auto-fallback')).toBeInTheDocument()
    expect(screen.getByText('Benchmark disabled')).toBeInTheDocument()
    expect(screen.queryByTestId('charts-view')).not.toBeInTheDocument()
    expect(screen.getByTestId('analysis-charts-placeholder')).toBeInTheDocument()

    await act(async () => {
      observerInstances[0].callback([
        { isIntersecting: true, target: screen.getByTestId('analysis-charts-anchor') } as unknown as IntersectionObserverEntry,
      ], {} as IntersectionObserver)
      await Promise.resolve()
    })

    expect(await screen.findByTestId('charts-view')).toBeInTheDocument()
  })

  it('shows empty state while loading or when no backtest is selected', () => {
    contextMock.mockReturnValueOnce({ results: null, loading: true })
    const { rerender } = render(<BacktestAnalysisPage />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()

    contextMock.mockReturnValueOnce({ results: null, loading: false })
    rerender(<BacktestAnalysisPage />)

    expect(screen.getByText('Select a backtest to view results')).toBeInTheDocument()
  })
})
