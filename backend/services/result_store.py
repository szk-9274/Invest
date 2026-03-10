from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger


OUTPUT_DIR_ENV_VAR = "INVEST_OUTPUT_DIR"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "python" / "output" / "backtest"
PINNED_BACKTEST_PERIODS = (
    "2020-01-01 to 2020-12-31",
    "2021-01-01 to 2021-12-31",
    "2022-01-01 to 2022-12-31",
    "2023-01-01 to 2023-12-31",
    "2024-01-01 to 2024-12-31",
    "2025-01-01 to 2025-12-31",
)
PINNED_BACKTEST_PERIOD_ORDER = {
    period: index for index, period in enumerate(PINNED_BACKTEST_PERIODS)
}


def get_backtest_output_dir() -> Path:
    override = os.getenv(OUTPUT_DIR_ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_OUTPUT_DIR


@dataclass(frozen=True)
class BacktestRun:
    dir_name: str
    result_dir: Path
    start_date: str
    end_date: str
    timestamp: str
    period: str
    trade_count: int
    trades_path: Optional[Path]
    trade_log_path: Optional[Path]
    ticker_stats_path: Optional[Path]
    charts_dir: Optional[Path]
    manifest_path: Optional[Path] = None
    run_label: Optional[str] = None
    experiment_name: Optional[str] = None
    strategy_name: Optional[str] = None
    benchmark_enabled: Optional[bool] = None
    rule_profile: Optional[str] = None
    tags: list[str] | None = None
    headline_metrics: dict | None = None
    has_displayable_results: bool = False


class ResultStore:
    def __init__(self, output_dir: Optional[str | Path] = None) -> None:
        self.output_dir = Path(output_dir).resolve() if output_dir else get_backtest_output_dir()
        self._snapshot: Optional[tuple[tuple[str, int], ...]] = None
        self._runs: list[BacktestRun] = []

    def list_runs(self) -> list[BacktestRun]:
        self._ensure_cache()
        return list(self._runs)

    def list_backtests(self) -> list[dict]:
        pinned_runs: dict[str, BacktestRun] = {}
        pinned_counts: dict[str, int] = {}
        regular_runs: list[BacktestRun] = []

        for run in self.list_runs():
            if not run.has_displayable_results:
                continue
            if run.period in PINNED_BACKTEST_PERIOD_ORDER:
                pinned_counts[run.period] = pinned_counts.get(run.period, 0) + 1
                pinned_runs.setdefault(run.period, run)
                continue
            regular_runs.append(run)

        ordered_runs: list[tuple[BacktestRun, bool, int]] = []
        for period, run in sorted(
            pinned_runs.items(),
            key=lambda item: PINNED_BACKTEST_PERIOD_ORDER[item[0]],
            reverse=True,
        ):
            ordered_runs.append((run, True, pinned_counts.get(period, 1)))

        for run in regular_runs:
            ordered_runs.append((run, False, 1))

        return [
            {
                "timestamp": run.timestamp,
                "start_date": run.start_date,
                "end_date": run.end_date,
                "period": run.period,
                "trade_count": run.trade_count,
                "dir_name": run.dir_name,
                "is_pinned": is_pinned,
                "available_runs": available_runs,
                "run_label": run.run_label,
                "experiment_name": run.experiment_name,
                "strategy_name": run.strategy_name,
                "benchmark_enabled": run.benchmark_enabled,
                "rule_profile": run.rule_profile,
                "tags": run.tags or [],
                "headline_metrics": run.headline_metrics,
            }
            for run, is_pinned, available_runs in ordered_runs
        ]

    def get_latest_run(self) -> Optional[BacktestRun]:
        runs = self.list_runs()
        return self._pick_best_run(runs)

    def get_run_by_dir_name(self, dir_name: str) -> Optional[BacktestRun]:
        for run in self.list_runs():
            if run.dir_name == dir_name:
                return run
        return None

    def get_run_by_timestamp(self, timestamp: str) -> Optional[BacktestRun]:
        normalized = timestamp.strip()
        if not normalized:
            return None

        for run in self.list_runs():
            if run.timestamp == normalized or run.dir_name == normalized:
                return run
        return None

    def get_run_by_range(self, range_value: Optional[str]) -> Optional[BacktestRun]:
        runs = self.list_runs()
        if not runs:
            return None
        if not range_value:
            return self._pick_best_run(runs)

        normalized = range_value.strip()
        if not normalized or normalized.upper() == "ALL":
            return self._pick_best_run(runs)

        exact_matches = [run for run in runs if run.dir_name == normalized or run.timestamp == normalized]
        if exact_matches:
            return exact_matches[0]

        normalized_period = normalized.replace("_to_", " to ")
        period_matches = [run for run in runs if run.period == normalized_period]
        if period_matches:
            return self._pick_best_run(period_matches)

        if len(normalized) == 4 and normalized.isdigit():
            year_matches = [run for run in runs if run.start_date.startswith(normalized)]
            if year_matches:
                return self._pick_best_run(year_matches)

        return None

    def _ensure_cache(self) -> None:
        snapshot = self._build_snapshot()
        if snapshot == self._snapshot:
            return

        self._runs = self._scan_runs()
        self._snapshot = snapshot

    def _build_snapshot(self) -> tuple[tuple[str, int], ...]:
        if not self.output_dir.exists():
            return tuple()

        entries: list[tuple[str, int]] = []
        for child in self.output_dir.iterdir():
            if child.is_dir() and child.name.startswith("backtest_"):
                entries.append((child.name, child.stat().st_mtime_ns))
        entries.sort(reverse=True)
        return tuple(entries)

    def _scan_runs(self) -> list[BacktestRun]:
        if not self.output_dir.exists():
            logger.warning(f"Output directory not found: {self.output_dir}")
            return []

        runs: list[BacktestRun] = []
        for child in sorted(self.output_dir.iterdir(), key=lambda item: item.name, reverse=True):
            if not child.is_dir() or not child.name.startswith("backtest_"):
                continue

            parsed = self._parse_dir_name(child.name)
            if parsed is None:
                continue

            start_date, end_date, timestamp = parsed
            ticker_stats_path = child / "ticker_stats.csv"
            trades_path = child / "trades.csv"
            trade_log_path = child / "trade_log.csv"
            charts_dir = child / "charts"
            manifest_path = child / "run_manifest.json"
            manifest = self._load_manifest(manifest_path)
            spec = manifest.get("spec", {}) if isinstance(manifest.get("spec"), dict) else {}
            metrics = manifest.get("metrics", {}) if isinstance(manifest.get("metrics"), dict) else {}

            runs.append(
                BacktestRun(
                    dir_name=child.name,
                    result_dir=child,
                    start_date=start_date,
                    end_date=end_date,
                    timestamp=timestamp,
                    period=f"{start_date} to {end_date}",
                    trade_count=self._read_trade_count(ticker_stats_path),
                    trades_path=trades_path if trades_path.exists() else None,
                    trade_log_path=trade_log_path if trade_log_path.exists() else None,
                    ticker_stats_path=ticker_stats_path if ticker_stats_path.exists() else None,
                    charts_dir=charts_dir if charts_dir.exists() else None,
                    manifest_path=manifest_path if manifest_path.exists() else None,
                    run_label=manifest.get("run_label") or spec.get("run_label"),
                    experiment_name=manifest.get("experiment_name") or spec.get("experiment_name"),
                    strategy_name=manifest.get("strategy_name") or spec.get("strategy_name"),
                    benchmark_enabled=manifest.get("benchmark_enabled", spec.get("use_benchmark")),
                    rule_profile=manifest.get("rule_profile") or spec.get("rule_profile"),
                    tags=manifest.get("tags") or spec.get("tags") or [],
                    headline_metrics=self._build_headline_metrics(metrics, start_date, end_date),
                    has_displayable_results=(
                        trades_path.exists()
                        or trade_log_path.exists()
                        or ticker_stats_path.exists()
                        or (charts_dir.exists() and any(charts_dir.iterdir()))
                        or bool(metrics)
                    ),
                )
            )
        return runs

    @staticmethod
    def _pick_best_run(runs: list[BacktestRun]) -> Optional[BacktestRun]:
        if not runs:
            return None
        for run in runs:
            if run.has_displayable_results:
                return run
        return runs[0]

    @staticmethod
    def _build_headline_metrics(metrics: dict, start_date: str, end_date: str) -> dict | None:
        if not metrics:
            return None

        total_return_pct = float(metrics.get("total_return_pct", 0) or 0)
        annual_return_pct = metrics.get("annual_return_pct")
        if annual_return_pct is None:
            annual_return_pct = ResultStore._annualize_return(total_return_pct, start_date, end_date)

        information_ratio = metrics.get("information_ratio")
        if information_ratio is None:
            information_ratio = metrics.get("sharpe_ratio", 0)

        return {
            "total_trades": int(metrics.get("total_trades", 0) or 0),
            "total_pnl": float(metrics.get("total_pnl", 0) or 0),
            "win_rate": float(metrics.get("win_rate", 0) or 0),
            "annual_return_pct": float(annual_return_pct or 0),
            "information_ratio": float(information_ratio or 0),
            "max_drawdown_pct": float(metrics.get("max_drawdown_pct", 0) or 0),
        }

    @staticmethod
    def _annualize_return(total_return_pct: float, start_date: str, end_date: str) -> float:
        try:
            start = pd.Timestamp(start_date)
            end = pd.Timestamp(end_date)
        except (TypeError, ValueError):
            return total_return_pct

        days = max((end - start).days, 0)
        if days == 0 or total_return_pct <= -1:
            return total_return_pct

        years = days / 365.25
        if years <= 0:
            return total_return_pct

        return (1 + total_return_pct) ** (1 / years) - 1

    @staticmethod
    def _parse_dir_name(dir_name: str) -> Optional[tuple[str, str, str]]:
        if not dir_name.startswith("backtest_"):
            return None
        try:
            payload = dir_name.replace("backtest_", "", 1)
            start_date, remaining = payload.split("_to_", 1)
            end_date, timestamp = remaining.split("_", 1)
        except ValueError:
            logger.warning(f"Failed to parse backtest directory name: {dir_name}")
            return None
        return start_date, end_date, timestamp

    @staticmethod
    def _read_trade_count(ticker_stats_path: Path) -> int:
        if not ticker_stats_path.exists():
            return 0
        try:
            df = pd.read_csv(ticker_stats_path)
        except (OSError, ValueError, pd.errors.EmptyDataError) as exc:
            logger.warning(f"Failed to read ticker stats from {ticker_stats_path}: {exc}")
            return 0
        return len(df.index)

    @staticmethod
    def _load_manifest(manifest_path: Path) -> dict:
        if not manifest_path.exists():
            return {}
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            logger.warning(f"Failed to read run manifest from {manifest_path}: {exc}")
            return {}
