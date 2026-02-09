/**
 * Chart Page
 *
 * Displays a TradingView-style candlestick chart for a selected ticker.
 * Uses Plotly for rendering (Phase B-2 will enhance this).
 */
import React from 'react'

interface ChartProps {
  ticker: string
  onBack?: () => void
}

export function Chart({ ticker, onBack }: ChartProps) {
  return (
    <div data-testid="chart-page">
      <header>
        {onBack && (
          <button onClick={onBack} data-testid="back-button">
            Back
          </button>
        )}
        <h1 data-testid="chart-title">{ticker} Chart</h1>
      </header>

      <div data-testid="chart-container">
        {/* Plotly chart will be rendered here in Phase B-2 */}
        <p>Chart for {ticker} will be displayed here</p>
      </div>
    </div>
  )
}
