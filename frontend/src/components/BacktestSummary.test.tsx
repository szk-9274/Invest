import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BacktestSummary } from './BacktestSummary'

describe('BacktestSummary', () => {
  it('shows a loading state', () => {
    render(<BacktestSummary data={null} loading />)

    expect(screen.getByText('Loading metrics...')).toBeInTheDocument()
  })

  it('shows an empty state when no summary is available', () => {
    render(<BacktestSummary data={null} />)

    expect(screen.getByText('No data available')).toBeInTheDocument()
  })

  it('renders formatted metrics and a positive profit factor', () => {
    render(
      <BacktestSummary
        data={{
          total_trades: 12,
          winning_trades: 7,
          losing_trades: 5,
          win_rate: 0.5833,
          total_pnl: 1500,
          avg_win: 300,
          avg_loss: -100,
        }}
      />,
    )

    expect(screen.getByText('Total P&L')).toBeInTheDocument()
    expect(screen.getByText('$1,500.00')).toBeInTheDocument()
    expect(screen.getByText('58.33%')).toBeInTheDocument()
    expect(screen.getByText('7W / 5L')).toBeInTheDocument()
    expect(screen.getByText('3.00')).toBeInTheDocument()
  })

  it('renders advanced headline metrics when available', () => {
    render(
      <BacktestSummary
        data={{
          total_trades: 12,
          winning_trades: 7,
          losing_trades: 5,
          win_rate: 0.5833,
          total_pnl: 1500,
          avg_win: 300,
          avg_loss: -100,
          final_capital: 101500,
          annual_return_pct: 0.18,
          information_ratio: 1.25,
          max_drawdown_pct: -0.08,
        }}
      />,
    )

    expect(screen.getByText('Annual Return')).toBeInTheDocument()
    expect(screen.getByText('18.00%')).toBeInTheDocument()
    expect(screen.getByText('Information Ratio')).toBeInTheDocument()
    expect(screen.getByText('-8.00%')).toBeInTheDocument()
    expect(screen.getByText('$101,500.00')).toBeInTheDocument()
  })

  it('falls back to N/A when profit factor cannot be calculated', () => {
    render(
      <BacktestSummary
        data={{
          total_trades: 2,
          winning_trades: 1,
          losing_trades: 1,
          win_rate: 0.5,
          total_pnl: -20,
          avg_win: 10,
          avg_loss: 0,
        }}
      />,
    )

    expect(screen.getByText('N/A')).toBeInTheDocument()
  })

  it('renders a negative profit factor when losses outweigh wins', () => {
    render(
      <BacktestSummary
        data={{
          total_trades: 4,
          winning_trades: 1,
          losing_trades: 3,
          win_rate: 0.25,
          total_pnl: -120,
          avg_win: 50,
          avg_loss: -100,
        }}
      />,
    )

    expect(screen.getByText('0.50')).toHaveClass('metric-negative')
  })

  it('renders a neutral profit factor when it is between 1.00 and 1.49', () => {
    render(
      <BacktestSummary
        data={{
          total_trades: 5,
          winning_trades: 3,
          losing_trades: 2,
          win_rate: 0.6,
          total_pnl: 25,
          avg_win: 125,
          avg_loss: -100,
        }}
      />,
    )

    expect(screen.getByText('1.25')).toHaveClass('metric-neutral')
  })
})
