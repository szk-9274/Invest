import { buildApiUrl } from './base'
import type {
  BacktestHeadlineMetrics,
  BacktestListResponse,
  BacktestMetadata,
  BacktestResults,
  BacktestSummary,
  BacktestVisualization,
  TickerStats,
  TimeSeriesPoint,
  SignalEventPoint,
  TradeRecord,
} from './generated/contracts'

export type {
  BacktestHeadlineMetrics,
  BacktestMetadata,
  BacktestResults,
  BacktestSummary,
  BacktestVisualization,
  SignalEventPoint,
  TickerStats,
  TimeSeriesPoint,
  TradeRecord,
}

/**
 * Fetch latest backtest results
 */
export async function fetchLatestBacktest(): Promise<BacktestResults> {
  const response = await fetch(buildApiUrl('/backtest/latest'));
  if (!response.ok) {
    throw new Error(`Failed to fetch latest backtest: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch backtest results by timestamp
 */
export async function fetchBacktestResults(timestamp: string): Promise<BacktestResults> {
  const response = await fetch(buildApiUrl(`/backtest/results/${timestamp}`));
  if (!response.ok) {
    throw new Error(`Failed to fetch backtest results: ${response.statusText}`);
  }
  return response.json();
}

/**
 * List all available backtests
 */
export async function listAllBacktests(): Promise<BacktestMetadata[]> {
  const response = await fetch(buildApiUrl('/backtest/list'));
  if (!response.ok) {
    throw new Error(`Failed to list backtests: ${response.statusText}`);
  }
  const data = (await response.json()) as BacktestListResponse;
  return data.backtests;
}
