/**
 * Backtest API Communication Layer
 */

export interface BacktestSummary {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_pnl: number;
  avg_win: number;
  avg_loss: number;
}

export interface TradeRecord {
  ticker: string;
  entry_date: string;
  entry_price: number;
  exit_date: string;
  exit_price: number;
  exit_reason: string;
  shares: number;
  pnl: number;
  pnl_pct: number;
}

export interface TickerStats {
  ticker: string;
  total_pnl: number;
  trade_count: number;
}

export interface BacktestResults {
  timestamp: string;
  summary: BacktestSummary;
  trades: TradeRecord[];
  ticker_stats: TickerStats[];
  charts: Record<string, string | null>;
}

export interface BacktestMetadata {
  timestamp: string;
  start_date: string;
  end_date: string;
  period: string;
  trade_count: number;
  dir_name: string;
}

type ApiImportMetaEnv = {
  VITE_API_URL?: string;
};

const configuredApiBaseUrl = ((import.meta as { env?: ApiImportMetaEnv }).env?.VITE_API_URL ?? '').trim();
const API_BASE_URL = (configuredApiBaseUrl || '/api').replace(/\/$/, '');

/**
 * Fetch latest backtest results
 */
export async function fetchLatestBacktest(): Promise<BacktestResults> {
  const response = await fetch(`${API_BASE_URL}/backtest/latest`);
  if (!response.ok) {
    throw new Error(`Failed to fetch latest backtest: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch backtest results by timestamp
 */
export async function fetchBacktestResults(timestamp: string): Promise<BacktestResults> {
  const response = await fetch(`${API_BASE_URL}/backtest/results/${timestamp}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch backtest results: ${response.statusText}`);
  }
  return response.json();
}

/**
 * List all available backtests
 */
export async function listAllBacktests(): Promise<BacktestMetadata[]> {
  const response = await fetch(`${API_BASE_URL}/backtest/list`);
  if (!response.ok) {
    throw new Error(`Failed to list backtests: ${response.statusText}`);
  }
  const data = await response.json();
  return data.backtests;
}
