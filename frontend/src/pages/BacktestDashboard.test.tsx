import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { BacktestDashboard } from './BacktestDashboard'
import { BacktestAnalysisPage } from './BacktestAnalysisPage'
import { BacktestRunPage } from './BacktestRunPage'

const {
  listAllBacktestsMock,
  fetchBacktestResultsMock,
  fetchLatestBacktestMock,
  createJobMock,
  getJobMock,
  getJobLogsMock,
  cancelJobMock,
} = vi.hoisted(() => ({
  listAllBacktestsMock: vi.fn(),
  fetchBacktestResultsMock: vi.fn(),
  fetchLatestBacktestMock: vi.fn(),
  createJobMock: vi.fn(),
  getJobMock: vi.fn(),
  getJobLogsMock: vi.fn(),
  cancelJobMock: vi.fn(),
}))

vi.mock('../api/backtest', () => ({
  listAllBacktests: listAllBacktestsMock,
  fetchBacktestResults: fetchBacktestResultsMock,
  fetchLatestBacktest: fetchLatestBacktestMock,
}))

vi.mock('../api/jobs', () => ({
  createJob: createJobMock,
  getJob: getJobMock,
  getJobLogs: getJobLogsMock,
  cancelJob: cancelJobMock,
}))

vi.mock('../components/BacktestSummary', () => ({
  BacktestSummary: ({ data, loading }: { data: { total_trades?: number } | null; loading?: boolean }) => (
    <div data-testid="summary-view">{loading ? 'loading' : data?.total_trades ?? 'empty'}</div>
  ),
}))

vi.mock('../components/TradeTable', () => ({
  TradeTable: ({ trades, loading }: { trades: unknown[]; loading?: boolean }) => (
    <div data-testid="trades-view">{loading ? 'loading' : trades.length}</div>
  ),
}))

vi.mock('../components/RunPanel', () => ({
  RunPanel: ({
    onRun,
    onCancel,
    activeJob,
    logs,
    runError,
  }: {
    onRun: (request: { command: 'backtest'; start_date: string; end_date: string }) => Promise<void>
    onCancel: () => Promise<void>
    activeJob: { status?: string } | null
    logs: string[]
    runError: string | null
  }) => (
    <div data-testid="run-panel">
      <button type="button" onClick={() => void onRun({ command: 'backtest', start_date: '2024-01-01', end_date: '2024-01-31' })}>
        Run job
      </button>
      <button type="button" onClick={() => void onCancel()}>
        Cancel job
      </button>
      <span data-testid="run-panel-status">{activeJob?.status ?? 'none'}</span>
      <span data-testid="run-panel-logs">{logs.join('|') || 'no-logs'}</span>
      {runError && <span data-testid="run-panel-error">{runError}</span>}
    </div>
  ),
}))

vi.mock('../components/Notification', () => ({
  Notification: ({
    message,
    onDismiss,
  }: {
    message: string
    onDismiss: () => void
  }) => (
    <div data-testid="notification">
      <span>{message}</span>
      <button type="button" onClick={onDismiss}>
        Dismiss notification
      </button>
    </div>
  ),
}))

vi.mock('../components/BacktestStatus', () => ({
  BacktestStatus: ({
    activeJob,
    logs,
  }: {
    activeJob: { status?: string } | null
    logs: string[]
  }) => <div data-testid="backtest-status">{activeJob?.status ?? 'idle'}:{logs.length}</div>,
}))

vi.mock('../components/TopBottomPurchaseCharts', () => ({
  TopBottomPurchaseCharts: ({ trades }: { trades: unknown[] }) => (
    <div data-testid="charts-view">charts:{trades.length}</div>
  ),
}))

const sampleBacktests = [
  {
    timestamp: 'backtest_2025-01-01_to_2025-12-31_20251231-235959',
    start_date: '2025-01-01',
    end_date: '2025-12-31',
    period: '2025-01-01 to 2025-12-31',
    trade_count: 2,
    dir_name: 'run-2025',
    is_pinned: true,
    available_runs: 3,
  },
  {
    timestamp: 'backtest_2026-01-01_to_2026-01-31_20260131-000000',
    start_date: '2026-01-01',
    end_date: '2026-01-31',
    period: '2026-01-01 to 2026-01-31',
    trade_count: 2,
    dir_name: 'run-a',
    is_pinned: false,
    available_runs: 1,
  },
]

const sampleResults = {
  timestamp: 'backtest_2025-01-01_to_2025-12-31_20251231-235959',
  summary: {
    total_trades: 2,
    winning_trades: 1,
    losing_trades: 1,
    win_rate: 0.5,
    total_pnl: 10,
    avg_win: 15,
    avg_loss: -5,
  },
  trades: [
    { ticker: 'AAA', entry_date: '2026-01-01', exit_date: '2026-01-02' },
    { ticker: 'BBB', entry_date: '2026-01-03', exit_date: '2026-01-04' },
  ],
  ticker_stats: [{ ticker: 'AAA', total_pnl: 10, trade_count: 1 }],
  charts: {},
}

const runningJob = {
  job_id: 'job-1',
  command: 'backtest',
  command_line: 'python run.py',
  status: 'running',
  created_at: '2026-01-01T00:00:00Z',
  started_at: '2026-01-01T00:00:05Z',
  finished_at: null,
  return_code: null,
  error: null,
  timeout_seconds: 600,
}

let consoleErrorSpy: {
  mock: { calls: unknown[][] }
  mockRestore: () => void
}

async function flushAsyncUpdates() {
  await Promise.resolve()
  await Promise.resolve()
}

async function clickAndFlush(user: ReturnType<typeof userEvent.setup>, target: Element) {
  await act(async () => {
    await user.click(target)
    await flushAsyncUpdates()
  })
}

function LocationDisplay() {
  const location = useLocation()
  return <div data-testid="location-display">{location.pathname}</div>
}

function renderDashboard(initialEntry = '/dashboard') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <LocationDisplay />
      <Routes>
        <Route path="/dashboard" element={<BacktestDashboard />}>
          <Route index element={<Navigate to="run" replace />} />
          <Route path="run" element={<BacktestRunPage />} />
          <Route path="analysis" element={<BacktestAnalysisPage />} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

describe('BacktestDashboard', () => {
  beforeEach(() => {
    vi.useRealTimers()
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    Object.defineProperty(window, 'innerWidth', {
      configurable: true,
      writable: true,
      value: 1280,
    })

    listAllBacktestsMock.mockReset()
    fetchBacktestResultsMock.mockReset()
    fetchLatestBacktestMock.mockReset()
    createJobMock.mockReset()
    getJobMock.mockReset()
    getJobLogsMock.mockReset()
    cancelJobMock.mockReset()

    listAllBacktestsMock.mockResolvedValue(sampleBacktests)
    fetchBacktestResultsMock.mockResolvedValue(sampleResults)
    fetchLatestBacktestMock.mockResolvedValue({
      ...sampleResults,
      timestamp: 'backtest_2026-02-01_to_2026-02-28_20260228-000000',
    })
    createJobMock.mockResolvedValue(runningJob)
    getJobMock.mockResolvedValue({ ...runningJob, status: 'succeeded' })
    getJobLogsMock.mockResolvedValue({ job_id: 'job-1', status: 'running', lines: ['line-a', 'line-b'] })
    cancelJobMock.mockResolvedValue({ ...runningJob, status: 'cancelled' })
  })

  afterEach(() => {
    expect(
      consoleErrorSpy.mock.calls.filter(
        ([message]) =>
          typeof message === 'string'
          && (message.includes('not wrapped in act') || message.includes('suspended resource finished loading')),
      ),
    ).toEqual([])
    vi.unstubAllGlobals()
    consoleErrorSpy.mockRestore()
    vi.useRealTimers()
  })

  it('redirects /dashboard to the run route and renders execution content', async () => {
    renderDashboard()

    expect(await screen.findByRole('heading', { name: 'Backtest Dashboard' })).toBeInTheDocument()
    expect(screen.getByTestId('location-display')).toHaveTextContent('/dashboard/run')
    expect((await screen.findAllByText('2025-01-01 to 2025-12-31')).length).toBeGreaterThan(0)
    expect(screen.getByText('Pinned')).toBeInTheDocument()
    expect(screen.getByText(/Pinned annual results stay visible by default\./)).toBeInTheDocument()
    expect(screen.getByText('3 runs')).toBeInTheDocument()
    expect(await screen.findByTestId('run-panel')).toBeInTheDocument()
    expect(screen.getByTestId('backtest-status')).toHaveTextContent('idle:0')
  })

  it('loads the latest results, runs commands, and cancels commands', async () => {
    const user = userEvent.setup()

    renderDashboard('/dashboard/run')

    expect(await screen.findByTestId('run-panel')).toBeInTheDocument()

    await clickAndFlush(user, await screen.findByRole('button', { name: /Load Latest|Loading\.\.\./ }))
    await waitFor(() => expect(fetchLatestBacktestMock).toHaveBeenCalledTimes(1))

    await clickAndFlush(user, screen.getAllByRole('button', { name: 'Run job' })[0])
    await waitFor(() => expect(createJobMock).toHaveBeenCalledWith({
      command: 'backtest',
      start_date: '2024-01-01',
      end_date: '2024-01-31',
    }))
    expect(await screen.findByTestId('run-panel-status')).toHaveTextContent('running')
    expect(screen.getByTestId('run-panel-logs')).toHaveTextContent('line-a|line-b')

    await clickAndFlush(user, screen.getAllByRole('button', { name: 'Cancel job' })[0])
    await waitFor(() => expect(cancelJobMock).toHaveBeenCalledWith('job-1'))
  })

  it('polls job status and refreshes latest results when a running job succeeds', async () => {
    renderDashboard('/dashboard/run')

    expect(await screen.findByTestId('run-panel')).toBeInTheDocument()

    vi.useFakeTimers()
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTimeAsync })
    await clickAndFlush(user, screen.getAllByRole('button', { name: 'Run job' })[0])
    expect(createJobMock).toHaveBeenCalledTimes(1)

    await act(async () => {
      await vi.advanceTimersByTimeAsync(2000)
      await flushAsyncUpdates()
    })

    expect(getJobMock).toHaveBeenCalledWith('job-1')
    expect(fetchLatestBacktestMock).toHaveBeenCalledTimes(1)
  }, 10000)

  it('renders analysis route with summary, charts, and trades together', async () => {
    vi.stubGlobal('IntersectionObserver', undefined)
    renderDashboard('/dashboard/analysis')

    expect(await screen.findByTestId('summary-view')).toHaveTextContent('2')
    expect(await screen.findByTestId('charts-view')).toHaveTextContent('charts:2')
    expect(await screen.findByTestId('trades-view')).toHaveTextContent('2')
    expect(screen.queryByTestId('run-panel')).not.toBeInTheDocument()
  })

  it('shows and dismisses load errors', async () => {
    const user = userEvent.setup()
    listAllBacktestsMock.mockRejectedValueOnce(new Error('network down'))

    renderDashboard('/dashboard/run')

    expect(await screen.findByTestId('notification')).toHaveTextContent('Failed to load backtest list')

    await clickAndFlush(user, screen.getByRole('button', { name: 'Dismiss notification' }))
    await waitFor(() => expect(screen.queryByTestId('notification')).not.toBeInTheDocument())
  })
})
