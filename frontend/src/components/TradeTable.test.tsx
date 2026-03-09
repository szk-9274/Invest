import { act, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { TradeTable } from './TradeTable'
import type { TradeRecord } from '../api/backtest'

function buildTrade(index: number, overrides: Partial<TradeRecord> = {}): TradeRecord {
  return {
    ticker: `TICKER-${String(index).padStart(2, '0')}`,
    entry_date: `2024-01-${String((index % 28) + 1).padStart(2, '0')}`,
    entry_price: 100 + index,
    exit_date: `2024-02-${String((index % 28) + 1).padStart(2, '0')}`,
    exit_price: 110 + index,
    exit_reason: index % 2 === 0 ? 'target' : 'stop',
    shares: index + 1,
    pnl: index % 2 === 0 ? index * 10 : -index * 10,
    pnl_pct: index % 2 === 0 ? index / 100 : -index / 100,
    ...overrides,
  }
}

describe('TradeTable', () => {
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
  })

  afterEach(() => {
    expect(
      consoleErrorSpy.mock.calls.filter(
        ([message]) => typeof message === 'string' && message.includes('not wrapped in act'),
      ),
    ).toEqual([])
    consoleErrorSpy.mockRestore()
  })

  it('shows loading and empty states', () => {
    const { rerender } = render(<TradeTable trades={[]} loading />)
    expect(screen.getByText('Loading trades...')).toBeInTheDocument()

    rerender(<TradeTable trades={[]} />)
    expect(screen.getByText('No trades found')).toBeInTheDocument()
  })

  it('sorts and paginates trade rows', async () => {
    const user = userEvent.setup()
    const trades = [
      buildTrade(1, { ticker: 'BBB' }),
      buildTrade(2, { ticker: 'AAA' }),
      ...Array.from({ length: 23 }, (_, index) => buildTrade(index + 3)),
    ]

    render(<TradeTable trades={trades} />)

    expect(screen.getByText('Showing 1 to 20 of 25 trades')).toBeInTheDocument()
    expect(screen.getByText('Page 1 of 2')).toBeInTheDocument()

    await clickAndFlush(user, screen.getByRole('button', { name: 'Next →' }))
    expect(screen.getByText('Page 2 of 2')).toBeInTheDocument()

    await clickAndFlush(user, screen.getByRole('button', { name: '← Previous' }))
    expect(screen.getByText('Page 1 of 2')).toBeInTheDocument()

    await clickAndFlush(user, screen.getByText('Ticker').closest('th')!)
    expect(within(screen.getAllByRole('row')[1]).getByText('TICKER-25')).toBeInTheDocument()

    await clickAndFlush(user, screen.getByText('Ticker').closest('th')!)
    expect(within(screen.getAllByRole('row')[1]).getByText('AAA')).toBeInTheDocument()

    await clickAndFlush(user, screen.getByText('Entry Price').closest('th')!)
    expect(within(screen.getAllByRole('row')[1]).getByText('$125.00')).toBeInTheDocument()
  })

  it('renders null values with safe fallbacks', () => {
    render(
      <TradeTable
        trades={[
          buildTrade(1, {
            ticker: 'NULLS',
            entry_date: null,
            entry_price: null,
            exit_date: null,
            exit_price: null,
            shares: null,
            pnl: null,
            pnl_pct: null,
            exit_reason: null,
          }),
        ]}
      />,
    )

    const row = screen.getAllByRole('row')[1]
    expect(within(row).getAllByText('-')).toHaveLength(4)
    expect(within(row).getAllByText('$0.00')).toHaveLength(3)
    expect(within(row).getByText('0.00%')).toBeInTheDocument()
  })
})
