import { describe, it, expect, vi } from 'vitest'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {
  TopBottomPurchaseCharts,
  buildTopBottomPurchaseCharts,
  calculateMarkerSize,
} from './TopBottomPurchaseCharts'
import { TradeRecord, TickerStats } from '../api/backtest'

vi.mock('./CandlestickChart', () => ({
  CandlestickChart: () => <div data-testid="candlestick-chart" />,
}))

const trades: TradeRecord[] = [
  {
    ticker: 'AAA',
    entry_date: '2024-01-01',
    entry_price: 100,
    exit_date: '2024-01-10',
    exit_price: 110,
    exit_reason: 'rule',
    shares: 2,
    pnl: 20,
    pnl_pct: 0.1,
  },
  {
    ticker: 'CCC',
    entry_date: '2024-01-03',
    entry_price: 50,
    exit_date: '2024-01-09',
    exit_price: 45,
    exit_reason: 'rule',
    shares: 4,
    pnl: -20,
    pnl_pct: -0.1,
  },
]

const stats: TickerStats[] = [
  { ticker: 'AAA', total_pnl: 300, trade_count: 3 },
  { ticker: 'BBB', total_pnl: 100, trade_count: 2 },
  { ticker: 'CCC', total_pnl: -200, trade_count: 4 },
]

describe('calculateMarkerSize', () => {
  it('returns larger size for larger amount', () => {
    const small = calculateMarkerSize(100)
    const large = calculateMarkerSize(10000)
    expect(large).toBeGreaterThan(small)
  })

  it('clamps invalid amount to minimum', () => {
    expect(calculateMarkerSize(-1)).toBe(6)
    expect(calculateMarkerSize(Number.NaN)).toBe(6)
  })
})

describe('buildTopBottomPurchaseCharts', () => {
  it('builds top and bottom ticker chart list', () => {
    const items = buildTopBottomPurchaseCharts(trades, stats, 1)
    expect(items).toHaveLength(2)
    expect(items[0].ticker).toBe('AAA')
    expect(items[0].group).toBe('top')
    expect(items[1].ticker).toBe('CCC')
    expect(items[1].group).toBe('bottom')
  })

  it('converts trade to purchase amount by entry_price * shares', () => {
    const items = buildTopBottomPurchaseCharts(trades, stats, 1)
    expect(items[0].purchases[0].amount).toBe(200)
  })

  it('does not duplicate tickers when total ticker count is small', () => {
    const items = buildTopBottomPurchaseCharts(trades, stats, 5)
    const tickers = items.map((item) => item.ticker)
    expect(new Set(tickers).size).toBe(tickers.length)
  })
})

describe('TopBottomPurchaseCharts', () => {
  it('shows empty state when no data', () => {
    render(<TopBottomPurchaseCharts trades={[]} tickerStats={[]} />)
    expect(screen.getByText('No purchase data available')).toBeInTheDocument()
  })

  it('renders chart cards when data exists', () => {
    render(<TopBottomPurchaseCharts trades={trades} tickerStats={stats} limit={1} />)
    expect(screen.getByTestId('purchase-charts')).toBeInTheDocument()
    expect(screen.getAllByTestId('purchase-chart-card')).toHaveLength(2)
    expect(screen.getAllByTestId('candlestick-chart')).toHaveLength(2)
  })

  it('opens an expanded lightbox when a chart is selected', async () => {
    const user = userEvent.setup()

    render(<TopBottomPurchaseCharts trades={trades} tickerStats={stats} limit={1} />)

    await act(async () => {
      await user.click(screen.getAllByRole('button', { name: /expand chart/i })[0])
    })

    expect(screen.getByRole('dialog', { name: /expand chart/i })).toBeInTheDocument()
  })
})
