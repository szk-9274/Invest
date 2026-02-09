/**
 * TickerList Component
 *
 * Displays a list of tickers (top winners or bottom losers)
 * with clickable items that navigate to chart view.
 */
import React from 'react'

export interface TickerItem {
  ticker: string
  total_pnl: number
  num_trades?: number
  win_rate?: number
}

interface TickerListProps {
  title: string
  tickers: TickerItem[]
  onTickerClick?: (ticker: string) => void
  variant?: 'winners' | 'losers'
}

export function TickerList({
  title,
  tickers,
  onTickerClick,
  variant = 'winners',
}: TickerListProps) {
  if (tickers.length === 0) {
    return (
      <div data-testid="ticker-list">
        <h3>{title}</h3>
        <p>No data available</p>
      </div>
    )
  }

  return (
    <div data-testid="ticker-list">
      <h3>{title}</h3>
      <ul>
        {tickers.map((item) => (
          <li
            key={item.ticker}
            onClick={() => onTickerClick?.(item.ticker)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter') onTickerClick?.(item.ticker)
            }}
            style={{ cursor: onTickerClick ? 'pointer' : 'default' }}
          >
            <span data-testid="ticker-symbol">{item.ticker}</span>
            <span
              data-testid="ticker-pnl"
              style={{
                color: variant === 'winners' ? '#26a69a' : '#ef5350',
              }}
            >
              {item.total_pnl >= 0 ? '+' : ''}
              {item.total_pnl.toFixed(2)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
