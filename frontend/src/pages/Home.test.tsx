import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { Home } from './Home'

const { runBacktestMock, getTopBottomTickersMock } = vi.hoisted(() => ({
  runBacktestMock: vi.fn(),
  getTopBottomTickersMock: vi.fn(),
}))

vi.mock('../api/client', () => ({
  runBacktest: runBacktestMock,
  getTopBottomTickers: getTopBottomTickersMock,
}))

vi.mock('../components/BacktestForm', () => ({
  BacktestForm: ({
    onSubmit,
    isLoading,
  }: {
    onSubmit: (startDate: string, endDate: string) => Promise<void>
    isLoading?: boolean
  }) => (
    <button
      type="button"
      data-testid="backtest-form-submit"
      disabled={Boolean(isLoading)}
      onClick={async () => {
        await onSubmit('2024-01-01', '2024-01-31')
      }}
    >
      Run mocked backtest
    </button>
  ),
}))

vi.mock('../components/TickerList', () => ({
  TickerList: ({
    title,
    tickers,
    onTickerClick,
    variant,
  }: {
    title: string
    tickers: Array<{ ticker: string }>
    onTickerClick?: (ticker: string) => void
    variant?: string
  }) => (
    <section data-testid={`${variant ?? 'default'}-list`}>
      <h2>{title}</h2>
      {tickers.length === 0 && <span>No data available</span>}
      {tickers.map((ticker) => (
        <button key={ticker.ticker} type="button" onClick={() => onTickerClick?.(ticker.ticker)}>
          {ticker.ticker}
        </button>
      ))}
    </section>
  ),
}))

describe('Home', () => {
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

  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    runBacktestMock.mockReset()
    getTopBottomTickersMock.mockReset()
    runBacktestMock.mockResolvedValue({ message: 'Backtest started' })
    getTopBottomTickersMock.mockResolvedValue({ top: [], bottom: [] })
  })

  afterEach(() => {
    expect(
      consoleErrorSpy.mock.calls.filter(
        ([message]) => typeof message === 'string' && message.includes('not wrapped in act'),
      ),
    ).toEqual([])
    consoleErrorSpy.mockRestore()
  })

  it('loads top and bottom tickers on mount', async () => {
    getTopBottomTickersMock.mockResolvedValue({
      top: [{ ticker: 'AAPL', total_pnl: 100, num_trades: null, win_rate: null }],
      bottom: [{ ticker: 'TSLA', total_pnl: -50, num_trades: 1, win_rate: 0.3 }],
    })

    render(<Home />)

    await waitFor(() => expect(getTopBottomTickersMock).toHaveBeenCalledTimes(1))

    expect(screen.getByText('MinerviLism Backtest')).toBeInTheDocument()
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('TSLA')).toBeInTheDocument()
  })

  it('submits a backtest and refreshes ticker lists', async () => {
    const user = userEvent.setup()

    render(<Home />)

    await waitFor(() => expect(getTopBottomTickersMock).toHaveBeenCalledTimes(1))
    await clickAndFlush(user, screen.getByTestId('backtest-form-submit'))

    await waitFor(() =>
      expect(runBacktestMock).toHaveBeenCalledWith({
        start_date: '2024-01-01',
        end_date: '2024-01-31',
      }),
    )

    expect(await screen.findByTestId('status-message')).toHaveTextContent('Backtest started')
    expect(getTopBottomTickersMock).toHaveBeenCalledTimes(2)
  })

  it('shows an error message when backtest submission fails', async () => {
    const user = userEvent.setup()
    runBacktestMock.mockRejectedValueOnce(new Error('boom'))

    render(<Home />)

    await waitFor(() => expect(getTopBottomTickersMock).toHaveBeenCalledTimes(1))
    await clickAndFlush(user, screen.getByTestId('backtest-form-submit'))

    expect(await screen.findByTestId('status-message')).toHaveTextContent(
      'Backtest failed. Please try again.',
    )
  })

  it('keeps the page rendered when ticker loading fails', async () => {
    getTopBottomTickersMock.mockRejectedValueOnce(new Error('network'))

    render(<Home />)

    await waitFor(() => expect(getTopBottomTickersMock).toHaveBeenCalledTimes(1))

    expect(screen.getByTestId('home-page')).toBeInTheDocument()
    expect(screen.getByText('MinerviLism Backtest')).toBeInTheDocument()
  })

  it('navigates when a ticker is clicked and a callback is provided', async () => {
    const user = userEvent.setup()
    const onNavigateToChart = vi.fn()
    getTopBottomTickersMock.mockResolvedValue({
      top: [{ ticker: 'AAPL', total_pnl: 100 }],
      bottom: [],
    })

    render(<Home onNavigateToChart={onNavigateToChart} />)

    await waitFor(() => expect(getTopBottomTickersMock).toHaveBeenCalledTimes(1))
    await clickAndFlush(user, screen.getByRole('button', { name: 'AAPL' }))

    expect(onNavigateToChart).toHaveBeenCalledWith('AAPL')
  })

  it('does not fail when a ticker is clicked without a callback', async () => {
    const user = userEvent.setup()
    getTopBottomTickersMock.mockResolvedValue({
      top: [{ ticker: 'AAPL', total_pnl: 100 }],
      bottom: [],
    })

    render(<Home />)

    await waitFor(() => expect(getTopBottomTickersMock).toHaveBeenCalledTimes(1))
    await clickAndFlush(user, screen.getByRole('button', { name: 'AAPL' }))

    expect(screen.getByTestId('home-page')).toBeInTheDocument()
  })
})
