import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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

const setSelectedTimestamp = vi.fn()

describe('BacktestRunPage', () => {
  it('renders pinned runs and allows selecting another run', async () => {
    const user = userEvent.setup()
    contextMock.mockReturnValue({
      backtests: [
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
        },
        {
          timestamp: 'run-2026',
          period: '2026 annual',
          trade_count: 8,
          is_pinned: false,
          available_runs: 1,
          run_label: 'comparison-b',
        },
      ],
      selectedTimestamp: 'run-2025',
      setSelectedTimestamp,
      activeJob: { status: 'running' },
      jobLogs: ['line-a'],
      runError: null,
      handleRunCommand: vi.fn(),
      handleCancelCommand: vi.fn(),
    })

    render(<BacktestRunPage />)

    expect(screen.getByTestId('run-panel')).toHaveTextContent('running:1')
    expect(screen.getByText('Pinned')).toBeInTheDocument()
    expect(screen.getByText('baseline-run')).toBeInTheDocument()
    expect(screen.getByText('qlib-inspired')).toBeInTheDocument()
    expect(screen.getByText('rule-based-stage2')).toBeInTheDocument()
    expect(screen.getByText('No benchmark')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /2026 annual/i })).toBeInTheDocument()

    await act(async () => {
      await user.click(screen.getByRole('button', { name: /2026 annual/i }))
    })

    expect(setSelectedTimestamp).toHaveBeenCalledWith('run-2026')
  })

  it('shows an empty state when no runs are available', () => {
    contextMock.mockReturnValue({
      backtests: [],
      selectedTimestamp: null,
      setSelectedTimestamp: vi.fn(),
      activeJob: null,
      jobLogs: [],
      runError: null,
      handleRunCommand: vi.fn(),
      handleCancelCommand: vi.fn(),
    })

    render(<BacktestRunPage />)

    expect(screen.getByText('No backtests found')).toBeInTheDocument()
  })
})
