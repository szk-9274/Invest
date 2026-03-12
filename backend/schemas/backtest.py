from typing import Optional

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    start_date: str
    end_date: str


class BacktestResponse(BaseModel):
    status: str
    message: str
    job_id: Optional[str] = None


class BacktestSummary(BaseModel):
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0
    total_pnl: float = 0
    avg_win: float = 0
    avg_loss: float = 0
    final_capital: float = 0
    total_return_pct: float = 0
    annual_return_pct: float = 0
    information_ratio: float = 0
    max_drawdown_pct: float = 0
    sharpe_ratio: float = 0


class TradeRecord(BaseModel):
    ticker: str
    entry_date: Optional[str] = None
    entry_price: Optional[float] = None
    exit_date: Optional[str] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    shares: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    date: Optional[str] = None
    action: Optional[str] = None
    price: Optional[float] = None


class TradeLogEvent(BaseModel):
    date: Optional[str] = None
    action: Optional[str] = None
    ticker: str
    price: Optional[float] = None
    shares: Optional[float] = None
    pnl: Optional[float] = None


class TickerStats(BaseModel):
    ticker: str
    total_pnl: float
    trade_count: Optional[int] = None
    num_trades: Optional[int] = None
    win_rate: Optional[float] = None


class BacktestRunInfo(BaseModel):
    run_id: str
    run_label: Optional[str] = None
    experiment_name: Optional[str] = None
    strategy_name: Optional[str] = None
    benchmark_enabled: Optional[bool] = None
    rule_profile: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class StrategyProfile(BaseModel):
    strategy_name: str
    display_name: str
    short_name: str
    title: str
    description: str
    icon_key: Optional[str] = None
    result_strategy_name: Optional[str] = None
    portrait_asset_key: Optional[str] = None
    experiment_name: Optional[str] = None
    rule_profile: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    is_trader_strategy: bool = False
    is_current_baseline: bool = False
    sort_order: int = 0


class BacktestHeadlineMetrics(BaseModel):
    total_trades: int = 0
    total_pnl: float = 0
    win_rate: float = 0
    annual_return_pct: float = 0
    information_ratio: float = 0
    max_drawdown_pct: float = 0


class TimeSeriesPoint(BaseModel):
    time: str
    value: float


class SignalEventPoint(BaseModel):
    time: str
    action: str
    signal: int
    ticker: str
    price: float
    pnl: Optional[float] = None
    label: Optional[str] = None


class BacktestVisualization(BaseModel):
    equity_curve: list[TimeSeriesPoint] = Field(default_factory=list)
    drawdown: list[TimeSeriesPoint] = Field(default_factory=list)
    signal_events: list[SignalEventPoint] = Field(default_factory=list)


class BacktestResults(BaseModel):
    timestamp: str
    summary: BacktestSummary
    trades: list[TradeRecord]
    ticker_stats: list[TickerStats]
    charts: dict[str, Optional[str]]
    chart_previews: dict[str, Optional[str]] = Field(default_factory=dict)
    run_metadata: Optional[BacktestRunInfo] = None
    visualization: BacktestVisualization = Field(default_factory=BacktestVisualization)


class BacktestArtifactsResponse(BaseModel):
    trade_log: list[TradeLogEvent]
    ticker_stats: list[TickerStats]
    has_results: bool


class BacktestMetadata(BaseModel):
    timestamp: str
    start_date: str
    end_date: str
    period: str
    trade_count: int
    dir_name: str
    is_pinned: bool = False
    available_runs: int = 1
    run_label: Optional[str] = None
    experiment_name: Optional[str] = None
    strategy_name: Optional[str] = None
    benchmark_enabled: Optional[bool] = None
    rule_profile: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    headline_metrics: Optional[BacktestHeadlineMetrics] = None


class BacktestListResponse(BaseModel):
    backtests: list[BacktestMetadata]


class StrategyProfileListResponse(BaseModel):
    strategies: list[StrategyProfile]


class TopBottomTickers(BaseModel):
    top: list[TickerStats] = Field(default_factory=list)
    bottom: list[TickerStats] = Field(default_factory=list)
