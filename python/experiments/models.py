from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class RunSpec:
    mode: str
    run_id: str
    run_label: str
    start_date: str
    end_date: str
    use_benchmark: bool
    ticker_count: int
    tickers: list[str]
    config_path: str
    rule_profile: str
    experiment_name: str
    strategy_name: str
    tags: list[str] = field(default_factory=list)
    no_charts: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunMetrics:
    total_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    final_capital: float = 0.0
    total_return_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunArtifacts:
    trades_csv: str = 'trades.csv'
    trade_log_csv: str = 'trade_log.csv'
    ticker_stats_csv: str = 'ticker_stats.csv'
    charts_dir: str = 'charts'

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BacktestRunManifest:
    spec: RunSpec
    metrics: RunMetrics
    artifacts: RunArtifacts
    diagnostics: dict[str, Any] = field(default_factory=dict)
    parameter_snapshot: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            'run_id': self.spec.run_id,
            'run_label': self.spec.run_label,
            'experiment_name': self.spec.experiment_name,
            'strategy_name': self.spec.strategy_name,
            'benchmark_enabled': self.spec.use_benchmark,
            'rule_profile': self.spec.rule_profile,
            'tags': list(self.spec.tags),
            'spec': self.spec.to_dict(),
            'metrics': self.metrics.to_dict(),
            'artifacts': self.artifacts.to_dict(),
            'diagnostics': self.diagnostics,
            'parameter_snapshot': self.parameter_snapshot,
        }
        return payload
