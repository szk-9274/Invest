/**
 * Tests for TickerList component
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TickerList, TickerItem } from './TickerList'

const mockTickers: TickerItem[] = [
  { ticker: 'AAPL', total_pnl: 5000.0 },
  { ticker: 'MSFT', total_pnl: 3000.0 },
  { ticker: 'GOOG', total_pnl: 2000.0 },
]

const mockLosers: TickerItem[] = [
  { ticker: 'BAD1', total_pnl: -2000.0 },
  { ticker: 'BAD2', total_pnl: -3000.0 },
]

describe('TickerList', () => {
  it('renders title', () => {
    render(<TickerList title="Top 5 Winners" tickers={mockTickers} />)
    expect(screen.getByText('Top 5 Winners')).toBeInTheDocument()
  })

  it('renders all ticker symbols', () => {
    render(<TickerList title="Top Winners" tickers={mockTickers} />)
    const symbols = screen.getAllByTestId('ticker-symbol')
    expect(symbols).toHaveLength(3)
    expect(symbols[0]).toHaveTextContent('AAPL')
    expect(symbols[1]).toHaveTextContent('MSFT')
    expect(symbols[2]).toHaveTextContent('GOOG')
  })

  it('renders P&L values', () => {
    render(<TickerList title="Top Winners" tickers={mockTickers} />)
    const pnls = screen.getAllByTestId('ticker-pnl')
    expect(pnls[0]).toHaveTextContent('+5000.00')
  })

  it('shows "No data available" when tickers is empty', () => {
    render(<TickerList title="Top Winners" tickers={[]} />)
    expect(screen.getByText(/no data available/i)).toBeInTheDocument()
  })

  it('calls onTickerClick when a ticker is clicked', async () => {
    const mockClick = vi.fn()
    const user = userEvent.setup()
    render(
      <TickerList title="Top Winners" tickers={mockTickers} onTickerClick={mockClick} />,
    )

    const firstItem = screen.getByText('AAPL').closest('li')!
    await user.click(firstItem)
    expect(mockClick).toHaveBeenCalledWith('AAPL')
  })

  it('displays negative P&L for losers', () => {
    render(<TickerList title="Bottom Losers" tickers={mockLosers} variant="losers" />)
    const pnls = screen.getAllByTestId('ticker-pnl')
    expect(pnls[0]).toHaveTextContent('-2000.00')
  })
})
