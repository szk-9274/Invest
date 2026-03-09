import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { RunPanel } from './RunPanel'

const baseProps = {
  onRun: vi.fn().mockResolvedValue(undefined),
  onCancel: vi.fn().mockResolvedValue(undefined),
  activeJob: null,
  logs: [],
  runError: null,
}

describe('RunPanel', () => {
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

  async function typeAndFlush(user: ReturnType<typeof userEvent.setup>, target: Element, value: string) {
    await act(async () => {
      await user.type(target, value)
      await flushAsyncUpdates()
    })
  }

  async function clearAndTypeAndFlush(user: ReturnType<typeof userEvent.setup>, target: Element, value: string) {
    await act(async () => {
      await user.clear(target)
      await user.type(target, value)
      await flushAsyncUpdates()
    })
  }

  async function selectAndFlush(user: ReturnType<typeof userEvent.setup>, target: Element, value: string) {
    await act(async () => {
      await user.selectOptions(target, value)
      await flushAsyncUpdates()
    })
  }

  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
  })

  afterEach(() => {
    expect(
      consoleErrorSpy.mock.calls.filter(
        ([message]) => typeof message === 'string' && message.includes('not wrapped in act'),
      ),
    ).toEqual([])
    consoleErrorSpy.mockRestore()
  })

  it('submits a backtest request with optional parameters', async () => {
    const onRun = vi.fn().mockResolvedValue(undefined)
    const user = userEvent.setup()

    render(<RunPanel {...baseProps} onRun={onRun} />)

    await typeAndFlush(user, screen.getByLabelText('Tickers (comma-separated, optional)'), 'AAPL,MSFT')
    await clickAndFlush(user, screen.getByLabelText('Skip chart generation (--no-charts)'))
    await clearAndTypeAndFlush(user, screen.getByLabelText('Timeout (seconds)'), '1800')
    await clickAndFlush(user, screen.getByRole('button', { name: 'Run Command' }))

    await waitFor(() => {
      expect(onRun).toHaveBeenCalledWith({
        command: 'backtest',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
        tickers: 'AAPL,MSFT',
        no_charts: true,
        timeout_seconds: 1800,
      })
    })
  })

  it('submits stage2, chart, and update_tickers requests', async () => {
    const onRun = vi.fn().mockResolvedValue(undefined)
    const user = userEvent.setup()

    render(<RunPanel {...baseProps} onRun={onRun} />)

    await selectAndFlush(user, screen.getByLabelText('Command'), 'stage2')
    await clickAndFlush(user, screen.getByLabelText('Include fundamentals (--with-fundamentals)'))
    await clickAndFlush(user, screen.getByRole('button', { name: 'Run Command' }))

    await selectAndFlush(user, screen.getByLabelText('Command'), 'chart')
    await clearAndTypeAndFlush(user, screen.getByLabelText('Ticker'), 'nvda')
    await clickAndFlush(user, screen.getByRole('button', { name: 'Run Command' }))

    await selectAndFlush(user, screen.getByLabelText('Command'), 'update_tickers')
    await clearAndTypeAndFlush(user, screen.getByLabelText('Min Market Cap'), '1000000')
    await typeAndFlush(user, screen.getByLabelText('Max Tickers (optional)'), '25')
    await clickAndFlush(user, screen.getByRole('button', { name: 'Run Command' }))

    await waitFor(() => expect(onRun).toHaveBeenCalledTimes(3))
    expect(onRun.mock.calls[0][0]).toEqual({
      command: 'stage2',
      timeout_seconds: 7200,
      with_fundamentals: true,
    })
    expect(onRun.mock.calls[1][0]).toEqual({
      command: 'chart',
      ticker: 'NVDA',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      timeout_seconds: 7200,
    })
    expect(onRun.mock.calls[2][0]).toEqual({
      command: 'update_tickers',
      timeout_seconds: 7200,
      min_market_cap: 1000000,
      max_tickers: 25,
    })
  })

  it('shows running state, errors, and cancel action', async () => {
    const onCancel = vi.fn().mockResolvedValue(undefined)
    const user = userEvent.setup()

    render(
      <RunPanel
        {...baseProps}
        onCancel={onCancel}
        activeJob={{
          job_id: 'job-1',
          command: 'backtest',
          command_line: 'python main.py --mode backtest',
          status: 'running',
          created_at: '2026-01-01T00:00:00Z',
          timeout_seconds: 7200,
        }}
        logs={['line 1', 'line 2']}
        runError="Runner failed"
      />,
    )

    expect(screen.getByText('Status: running')).toBeInTheDocument()
    expect(screen.getByText(/Job ID:/)).toBeInTheDocument()
    expect(screen.getByText((_, element) => element?.tagName === 'PRE' && element.textContent === 'line 1\nline 2')).toBeInTheDocument()

    await clickAndFlush(user, screen.getByRole('button', { name: 'Cancel Running Job' }))
    expect(onCancel).toHaveBeenCalledTimes(1)
  })
})
