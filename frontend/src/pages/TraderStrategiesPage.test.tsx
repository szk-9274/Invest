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
          strategy_name: 'minervini-trend',
          display_name: 'Mark Minervini',
          short_name: 'Minervini',
          title: 'Trend template leader',
          description: 'Uses the current baseline backtest results.',
          icon_key: 'target',
          experiment_name: 'minervini-stage2-baseline',
          result_strategy_name: 'rule-based-stage2',
          portrait_asset_key: 'minervini',
          is_current_baseline: true,
          rule_profile: 'trend-template',
          tags: ['trader-inspired'],
          is_trader_strategy: true,
          sort_order: 5,
        },
        {
          strategy_name: 'buffett-quality',
          display_name: 'Warren Buffett',
          short_name: 'Buffett',
          title: 'Quality compounders',
          description: 'Looks for durable businesses.',
          icon_key: 'brain',
          experiment_name: 'buffett-quality-inspired',
          result_strategy_name: 'buffett-quality',
          portrait_asset_key: 'buffett',
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
          result_strategy_name: 'soros-breakout',
          portrait_asset_key: 'soros',
          rule_profile: 'macro-breakout',
          tags: ['trader-inspired'],
          is_trader_strategy: true,
          sort_order: 20,
        },
      ],
    })
    listAllBacktestsMock.mockResolvedValue([
      {
        timestamp: 'baseline-run',
        start_date: '2020-01-01',
        end_date: '2020-12-31',
        period: '2020-01-01 to 2020-12-31',
        trade_count: 5,
        dir_name: 'baseline-run',
        strategy_name: 'rule-based-stage2',
      },
    ])
    fetchBacktestByRangeMock.mockResolvedValue({
      timestamp: 'baseline-run',
      summary: { total_trades: 5 },
      trades: [],
      ticker_stats: [],
      charts: {},
      visualization: { equity_curve: [], drawdown: [], signal_events: [] },
    })
  })

  it('renders strategy profiles and loads the selected trader result', async () => {
    render(<TraderStrategiesPage />)

    expect(screen.getByRole('button', { name: /マーク・ミネルヴィニ/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /ウォーレン・バフェット/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /ジョージ・ソロス/i })).toBeInTheDocument()
    expect(screen.getByRole('img', { name: /マーク・ミネルヴィニ/i })).toBeInTheDocument()
    expect(screen.getByRole('img', { name: /マーク・ミネルヴィニ/i })).toHaveAttribute('loading', 'lazy')
    expect(screen.getByText('Current baseline')).toBeInTheDocument()

    await waitFor(() => expect(listAllBacktestsMock).toHaveBeenCalledWith('rule-based-stage2'))
    expect(fetchBacktestByRangeMock).toHaveBeenCalledWith('ALL', 'rule-based-stage2')
    expect(await screen.findByTestId('trader-summary')).toHaveTextContent('5')
    expect(screen.getAllByText('トレンドテンプレート主導').length).toBeGreaterThan(0)
    expect(screen.getByText('52週高値圏の主導株を追い、相対力とブレイクアウトの質を重視します。')).toBeInTheDocument()
    expect(screen.getByText('2020-01-01 to 2020-12-31')).toBeInTheDocument()
    expect(screen.queryByText('Mark Minervini')).not.toBeInTheDocument()
  })
})
