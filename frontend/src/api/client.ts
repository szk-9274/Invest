/**
 * API Client for MinerviLism Backtest Backend
 *
 * Provides typed functions for all backend API endpoints.
 */

import { buildApiUrl } from './base'
import type {
  BacktestArtifactsResponse,
  BacktestRequest,
  BacktestResponse,
  ChartData,
  TopBottomTickers,
  TradeMarkerPoint,
  TradeMarkers,
} from './generated/contracts'

export type BacktestResults = BacktestArtifactsResponse
export type { BacktestRequest, BacktestResponse, ChartData, TopBottomTickers, TradeMarkers }
export type TradeMarker = TradeMarkerPoint

/**
 * Run a backtest with the given date range.
 */
export async function runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
  const response = await fetch(buildApiUrl('/backtest/run'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  if (!response.ok) {
    throw new Error(`Backtest run failed: ${response.status}`)
  }
  return response.json()
}

/**
 * Get backtest results (trade log and ticker stats).
 */
export async function getBacktestResults(): Promise<BacktestResults> {
  const response = await fetch(buildApiUrl('/backtest/results'))
  if (!response.ok) {
    throw new Error(`Failed to fetch results: ${response.status}`)
  }
  return response.json()
}

/**
 * Get top and bottom tickers by P&L.
 */
export async function getTopBottomTickers(): Promise<TopBottomTickers> {
  const response = await fetch(buildApiUrl('/backtest/tickers'))
  if (!response.ok) {
    throw new Error(`Failed to fetch tickers: ${response.status}`)
  }
  return response.json()
}

/**
 * Get OHLCV chart data for a ticker.
 */
export async function getChartData(
  ticker: string,
  startDate?: string,
  endDate?: string,
): Promise<ChartData> {
  const params = new URLSearchParams()
  if (startDate) params.set('start_date', startDate)
  if (endDate) params.set('end_date', endDate)

  const url = buildApiUrl(`/charts/${ticker}${params.toString() ? '?' + params.toString() : ''}`)
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`Failed to fetch chart data: ${response.status}`)
  }
  return response.json()
}

/**
 * Get trade markers for a ticker.
 */
export async function getTradeMarkers(ticker: string): Promise<TradeMarkers> {
  const response = await fetch(buildApiUrl(`/charts/${ticker}/trades`))
  if (!response.ok) {
    throw new Error(`Failed to fetch trade markers: ${response.status}`)
  }
  return response.json()
}
