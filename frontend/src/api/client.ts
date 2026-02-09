/**
 * API Client for Invest Backtest Backend
 *
 * Provides typed functions for all backend API endpoints.
 */

const API_BASE = '/api'

export interface BacktestRequest {
  start_date: string
  end_date: string
}

export interface BacktestResponse {
  status: string
  message: string
}

export interface TickerStat {
  ticker: string
  total_pnl: number
  num_trades?: number
  win_rate?: number
}

export interface TopBottomTickers {
  top: TickerStat[]
  bottom: TickerStat[]
}

export interface BacktestResults {
  trade_log: Record<string, unknown>[]
  ticker_stats: Record<string, unknown>[]
  has_results: boolean
}

export interface ChartData {
  ticker: string
  dates: string[]
  open: number[]
  high: number[]
  low: number[]
  close: number[]
  volume: number[]
  sma20?: (number | null)[]
  sma50?: (number | null)[]
  sma200?: (number | null)[]
}

export interface TradeMarker {
  date: string
  price: number
  pnl?: number
}

export interface TradeMarkers {
  entries: TradeMarker[]
  exits: TradeMarker[]
}

/**
 * Run a backtest with the given date range.
 */
export async function runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
  const response = await fetch(`${API_BASE}/backtest/run`, {
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
  const response = await fetch(`${API_BASE}/backtest/results`)
  if (!response.ok) {
    throw new Error(`Failed to fetch results: ${response.status}`)
  }
  return response.json()
}

/**
 * Get top and bottom tickers by P&L.
 */
export async function getTopBottomTickers(): Promise<TopBottomTickers> {
  const response = await fetch(`${API_BASE}/backtest/tickers`)
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

  const url = `${API_BASE}/charts/${ticker}${params.toString() ? '?' + params.toString() : ''}`
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
  const response = await fetch(`${API_BASE}/charts/${ticker}/trades`)
  if (!response.ok) {
    throw new Error(`Failed to fetch trade markers: ${response.status}`)
  }
  return response.json()
}
