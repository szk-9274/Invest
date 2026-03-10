/* eslint-disable */
// Auto-generated from FastAPI OpenAPI schema.

export type BacktestArtifactsResponse = {
  trade_log: Array<TradeLogEvent>;
  ticker_stats: Array<TickerStats>;
  has_results: boolean;
}

export type BacktestHeadlineMetrics = {
  total_trades?: number;
  total_pnl?: number;
  win_rate?: number;
  annual_return_pct?: number;
  information_ratio?: number;
  max_drawdown_pct?: number;
}

export type BacktestListResponse = {
  backtests: Array<BacktestMetadata>;
}

export type BacktestMetadata = {
  timestamp: string;
  start_date: string;
  end_date: string;
  period: string;
  trade_count: number;
  dir_name: string;
  is_pinned?: boolean;
  available_runs?: number;
  run_label?: string | null;
  experiment_name?: string | null;
  strategy_name?: string | null;
  benchmark_enabled?: boolean | null;
  rule_profile?: string | null;
  tags?: Array<string>;
  headline_metrics?: BacktestHeadlineMetrics | null;
}

export type BacktestRequest = {
  start_date: string;
  end_date: string;
}

export type BacktestResponse = {
  status: string;
  message: string;
  job_id?: string | null;
}

export type BacktestResults = {
  timestamp: string;
  summary: BacktestSummary;
  trades: Array<TradeRecord>;
  ticker_stats: Array<TickerStats>;
  charts: Record<string, string | null>;
  run_metadata?: BacktestRunInfo | null;
  visualization?: BacktestVisualization;
}

export type BacktestRunInfo = {
  run_id: string;
  run_label?: string | null;
  experiment_name?: string | null;
  strategy_name?: string | null;
  benchmark_enabled?: boolean | null;
  rule_profile?: string | null;
  tags?: Array<string>;
}

export type BacktestSummary = {
  total_trades?: number;
  winning_trades?: number;
  losing_trades?: number;
  win_rate?: number;
  total_pnl?: number;
  avg_win?: number;
  avg_loss?: number;
  final_capital?: number;
  total_return_pct?: number;
  annual_return_pct?: number;
  information_ratio?: number;
  max_drawdown_pct?: number;
  sharpe_ratio?: number;
}

export type BacktestVisualization = {
  equity_curve?: Array<TimeSeriesPoint>;
  drawdown?: Array<TimeSeriesPoint>;
  signal_events?: Array<SignalEventPoint>;
}

export type ChartData = {
  ticker: string;
  dates?: Array<string>;
  open?: Array<number>;
  high?: Array<number>;
  low?: Array<number>;
  close?: Array<number>;
  volume?: Array<number>;
  sma20?: Array<number | null>;
  sma50?: Array<number | null>;
  sma200?: Array<number | null>;
}

export type HTTPValidationError = {
  detail?: Array<ValidationError>;
}

export type JobCreateRequest = {
  command: "backtest" | "stage2" | "full" | "chart" | "update_tickers";
  start_date?: string | null;
  end_date?: string | null;
  tickers?: string | null;
  no_charts?: boolean;
  ticker?: string | null;
  with_fundamentals?: boolean;
  min_market_cap?: number | null;
  max_tickers?: number | null;
  timeout_seconds?: number;
}

export type JobLogsResponse = {
  job_id: string;
  status: string;
  lines: Array<string>;
}

export type JobResponse = {
  job_id: string;
  command: string;
  command_line: string;
  status: "queued" | "running" | "succeeded" | "failed" | "cancelled" | "timeout";
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
  return_code?: number | null;
  error?: string | null;
  timeout_seconds: number;
}

export type OhlcPoint = {
  time: string;
  open?: number | null;
  high?: number | null;
  low?: number | null;
  close?: number | null;
  volume?: number | null;
}

export type OhlcResponse = {
  data?: Array<OhlcPoint>;
}

export type SignalEventPoint = {
  time: string;
  action: string;
  signal: number;
  ticker: string;
  price: number;
  pnl?: number | null;
  label?: string | null;
}

export type TickerStats = {
  ticker: string;
  total_pnl: number;
  trade_count?: number | null;
  num_trades?: number | null;
  win_rate?: number | null;
}

export type TimeSeriesPoint = {
  time: string;
  value: number;
}

export type TopBottomTickers = {
  top?: Array<TickerStats>;
  bottom?: Array<TickerStats>;
}

export type TradeLogEvent = {
  date?: string | null;
  action?: string | null;
  ticker: string;
  price?: number | null;
  shares?: number | null;
  pnl?: number | null;
}

export type TradeMarkerPoint = {
  date: string;
  price: number;
  pnl?: number | null;
  holding_days?: number | null;
  entry_date?: string | null;
  entry_price?: number | null;
}

export type TradeMarkers = {
  entries?: Array<TradeMarkerPoint>;
  exits?: Array<TradeMarkerPoint>;
}

export type TradeRecord = {
  ticker: string;
  entry_date?: string | null;
  entry_price?: number | null;
  exit_date?: string | null;
  exit_price?: number | null;
  exit_reason?: string | null;
  shares?: number | null;
  pnl?: number | null;
  pnl_pct?: number | null;
  date?: string | null;
  action?: string | null;
  price?: number | null;
}

export type ValidationError = {
  loc: Array<string | number>;
  msg: string;
  type: string;
  input?: unknown;
  ctx?: Record<string, unknown>;
}
