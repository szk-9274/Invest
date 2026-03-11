import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { TraderStrategiesPage } from './TraderStrategiesPage'

const { contextMock, listAllBacktestsMock, fetchBacktestByRangeMock } = vi.hoisted(() => ({
  contextMock: vi.fn(),
  listAllBacktestsMock: vi.fn(),
  fetchBacktestByRangeMock: vi.fn(),
}))

vi.mock('./BacktestDashboard', () => ({
  useBacktestDashboardContext: () => contextMock(),
}))

vi.mock('../api/backtest', () => ({
  listAllBacktests: listAllBacktestsMock,
  fetchBacktestByRange: fetchBacktestByRangeMock,
}))

vi.mock('../components/BacktestSummary', () => ({
  BacktestSummary: ({ data }: { data: { total_trades?: number } | null }) => (
    <div data-testid="trader-summary">{data?.total_trades ?? 'empty'}</div>
  ),
}))

describe('TraderStrategiesPage', () => {
  beforeEach(() => {
    contextMock.mockReturnValue({
      setSelectedTimestamp: vi.fn(),
      strategyProfiles: [
        {
          strategy_name: 'buffett-quality',
          display_name: 'Warren Buffett',
          short_name: 'Buffett',
          title: 'Quality compounders',
          description: 'Looks for durable businesses.',
          icon_key: 'brain',
          experiment_name: 'buffett-quality-inspired',
          rule_profile: 'quality-compounder',
          tags: ['trader-inspired'],
          is_trader_strategy: true,
          sort_order: 10,
        },
        {
          strategy_name: 'soros-breakout',
          display_name: 'George Soros',
          short_name: 'Soros',
          title: 'Reflexive breakout momentum',
          description: 'Fast confirmation and quicker exits.',
          icon_key: 'bolt',
          experiment_name: 'soros-breakout-inspired',
          rule_profile: 'macro-breakout',
          tags: ['trader-inspired'],
          is_trader_strategy: true,
          sort_order: 20,
        },
      ],
    })
    listAllBacktestsMock.mockResolvedValue([
      {
        timestamp: 'buffett-run',
        start_date: '2020-01-01',
        end_date: '2020-12-31',
        period: '2020-01-01 to 2020-12-31',
        trade_count: 5,
        dir_name: 'buffett-run',
        strategy_name: 'buffett-quality',
      },
    ])
    fetchBacktestByRangeMock.mockResolvedValue({
      timestamp: 'buffett-run',
      summary: { total_trades: 5 },
      trades: [],
      ticker_stats: [],
      charts: {},
      visualization: { equity_curve: [], drawdown: [], signal_events: [] },
    })
  })

  it('renders strategy profiles and loads the selected trader result', async () => {
    render(<TraderStrategiesPage />)

    expect(screen.getByRole('button', { name: /ウォーレン・バフェット/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /ジョージ・ソロス/i })).toBeInTheDocument()

    await waitFor(() => expect(listAllBacktestsMock).toHaveBeenCalledWith('buffett-quality'))
    expect(fetchBacktestByRangeMock).toHaveBeenCalledWith('ALL', 'buffett-quality')
    expect(await screen.findByTestId('trader-summary')).toHaveTextContent('5')
    expect(screen.getAllByText('優良企業の複利成長').length).toBeGreaterThan(0)
    expect(screen.getByText('持続的な競争優位を持つ企業を探します。')).toBeInTheDocument()
    expect(screen.queryByText('Warren Buffett')).not.toBeInTheDocument()
  })
})
