import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { BacktestRunPage } from './BacktestRunPage'

const { contextMock } = vi.hoisted(() => ({
  contextMock: vi.fn(),
}))

vi.mock('./BacktestDashboard', () => ({
  useBacktestDashboardContext: () => contextMock(),
}))

vi.mock('../components/RunPanel', () => ({
  RunPanel: ({ activeJob, logs }: { activeJob: { status?: string } | null; logs: string[] }) => (
    <div data-testid="run-panel">{activeJob?.status ?? 'idle'}:{logs.length}</div>
  ),
}))

vi.mock('../components/BacktestSummary', () => ({
  BacktestSummary: () => <div data-testid="summary-view">summary-view</div>,
}))

const setSelectedTimestamp = vi.fn()

function renderPage() {
  return render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <BacktestRunPage />
    </MemoryRouter>,
  )
}

describe('BacktestRunPage', () => {
  it('keeps annual benchmark runs inside Experiment List and removes duplicate summary panels', async () => {
    const user = userEvent.setup()
    contextMock.mockReturnValue({
      backtests: [
        {
          timestamp: 'run-2020',
          period: '2020 annual',
          trade_count: 6,
          is_pinned: true,
          available_runs: 1,
          run_label: 'annual-2020',
          experiment_name: 'annual-pinned-2020',
          strategy_name: 'rule-based-stage2',
          rule_profile: 'strict-auto-fallback',
          headline_metrics: {
            annual_return_pct: 0.14,
            information_ratio: 0.9,
            max_drawdown_pct: -0.07,
          },
        },
        {
          timestamp: 'run-2025',
          period: '2025 annual',
          trade_count: 12,
          is_pinned: true,
          available_runs: 2,
          run_label: 'baseline-run',
          experiment_name: 'qlib-inspired',
          strategy_name: 'rule-based-stage2',
          rule_profile: 'strict-auto-fallback',
          benchmark_enabled: false,
          headline_metrics: {
            annual_return_pct: 0.18,
            information_ratio: 1.25,
            max_drawdown_pct: -0.08,
            total_pnl: 4200,
            win_rate: 0.58,
          },
        },
        {
          timestamp: 'run-2026',
          period: '2026 annual',
          trade_count: 8,
          is_pinned: false,
          available_runs: 1,
          run_label: 'comparison-b',
          headline_metrics: {
            annual_return_pct: 0.09,
            information_ratio: 0.82,
            max_drawdown_pct: -0.12,
            total_pnl: 1800,
            win_rate: 0.51,
          },
        },
      ],
      results: {
        summary: {
          total_trades: 12,
        },
      },
      loading: false,
      strategyProfiles: [],
      selectedTimestamp: 'run-2025',
      setSelectedTimestamp,
      activeJob: { status: 'running' },
      jobLogs: ['line-a'],
      runError: null,
      handleRunCommand: vi.fn(),
      handleCancelCommand: vi.fn(),
    })

    renderPage()

    expect(screen.getByTestId('run-panel')).toHaveTextContent('running:1')
    expect(screen.queryByTestId('summary-view')).not.toBeInTheDocument()
    expect(screen.queryByText('Overview')).not.toBeInTheDocument()
    expect(screen.queryByText('Pinned Annual Results')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /2020 annual/i })).toBeInTheDocument()
    expect(screen.getAllByText('Pinned').length).toBeGreaterThan(0)
    expect(screen.getAllByText('baseline-run').length).toBeGreaterThan(0)
    expect(screen.getAllByText('qlib-inspired').length).toBeGreaterThan(0)
    expect(screen.getAllByText('rule-based-stage2').length).toBeGreaterThan(0)
    expect(screen.getAllByText('No benchmark').length).toBeGreaterThan(0)
    expect(screen.getByText('Experiment List')).toBeInTheDocument()
    expect(screen.getByText('Condition Comparison')).toBeInTheDocument()
    expect(screen.getAllByText('Annual Return').length).toBeGreaterThan(0)
    expect(screen.getAllByText('18.00%').length).toBeGreaterThan(0)
    expect(screen.getAllByText('1.25').length).toBeGreaterThan(0)
    expect(screen.getByRole('button', { name: /2026 annual/i })).toBeInTheDocument()

    await act(async () => {
      await user.click(screen.getByRole('button', { name: /2026 annual/i }))
    })

    expect(setSelectedTimestamp).toHaveBeenCalledWith('run-2026')
  })

  it('shows an empty state when no runs are available', () => {
    contextMock.mockReturnValue({
      backtests: [],
      results: null,
      loading: false,
      strategyProfiles: [],
      selectedTimestamp: null,
      setSelectedTimestamp: vi.fn(),
      activeJob: null,
      jobLogs: [],
      runError: null,
      handleRunCommand: vi.fn(),
      handleCancelCommand: vi.fn(),
    })

    renderPage()

    expect(screen.getAllByText('No backtests found').length).toBeGreaterThan(0)
  })
})
