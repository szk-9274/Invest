"""
Backtest API Endpoints

Provides REST API for:
- Running backtests
- Retrieving results
- Getting top/bottom tickers
"""
import os
from typing import Dict, Optional
from pathlib import Path
import json

from fastapi import APIRouter, HTTPException
from loguru import logger
import pandas as pd

from services.result_loader import (
    load_trade_log,
    load_ticker_stats,
    get_top_bottom_tickers,
    get_chart_as_base64,
    list_available_backtests,
    load_backtest_summary,
    generate_placeholder_charts,
)
from services.job_runner import job_runner
from services.result_store import ResultStore, get_backtest_output_dir
from schemas.backtest import (
    BacktestArtifactsResponse,
    BacktestListResponse,
    BacktestMetadata,
    BacktestRequest,
    BacktestResponse,
    BacktestResults,
    BacktestRunInfo,
    BacktestSummary,
    BacktestVisualization,
    SignalEventPoint,
    TickerStats,
    TimeSeriesPoint,
    TopBottomTickers,
    TradeLogEvent,
    TradeRecord,
)
from schemas.charts import OhlcPoint, OhlcResponse

router = APIRouter(prefix="/api/backtest", tags=["backtest"])

# Default paths for result files
DEFAULT_OUTPUT_DIR = str(get_backtest_output_dir())


def run_backtest_task(start_date: str, end_date: str) -> Dict:
    """
    Execute backtest with the given date range.

    This function wraps the existing Python backtest logic.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Dict with status and message
    """
    logger.info(f"Backtest requested: {start_date} to {end_date}")
    job = job_runner.create_job(
        {
            "command": "backtest",
            "start_date": start_date,
            "end_date": end_date,
        }
    )
    return {
        "status": "started",
        "message": f"Backtest queued for {start_date} to {end_date}",
        "job_id": job["job_id"],
    }


def _normalize_trade_log_records(records: list[dict]) -> list[TradeLogEvent]:
    return [TradeLogEvent(**record) for record in records]


def _normalize_ticker_stats(records: list[dict]) -> list[TickerStats]:
    return [TickerStats(**record) for record in records]


def _normalize_trade_records(records: list[dict]) -> list[TradeRecord]:
    return [TradeRecord(**record) for record in records]


def _get_store_or_404(output_dir: Optional[str] = None) -> ResultStore:
    store = ResultStore(output_dir or DEFAULT_OUTPUT_DIR)
    if not store.list_runs():
        raise HTTPException(status_code=404, detail="No backtest results found")
    return store


def _resolve_requested_run(store: ResultStore, selector: Optional[str]):
    chosen = store.get_run_by_range(selector)
    if chosen is None:
        normalized = (selector or "").strip()
        if normalized and normalized.upper() != "ALL":
            raise HTTPException(
                status_code=404,
                detail=f"No backtest results found for selector: {normalized}",
            )
        raise HTTPException(status_code=404, detail="No backtest results found")
    return chosen


def load_results(output_dir: Optional[str] = None) -> BacktestArtifactsResponse:
    """
    Load backtest results from output directory.

    Args:
        output_dir: Path to output directory (defaults to DEFAULT_OUTPUT_DIR)

    Returns:
        Dict with trade_log, ticker_stats, and has_results flag
    """
    store = ResultStore(output_dir or DEFAULT_OUTPUT_DIR)
    latest_run = store.get_latest_run()
    if latest_run is None:
        return BacktestArtifactsResponse(trade_log=[], ticker_stats=[], has_results=False)

    trade_log_path = str(latest_run.trade_log_path or latest_run.trades_path or "")
    ticker_stats_path = str(latest_run.ticker_stats_path or "")

    trade_log = _normalize_trade_log_records(load_trade_log(trade_log_path))
    ticker_stats = _normalize_ticker_stats(load_ticker_stats(ticker_stats_path))

    has_results = len(trade_log) > 0 or len(ticker_stats) > 0

    return BacktestArtifactsResponse(
        trade_log=trade_log,
        ticker_stats=ticker_stats,
        has_results=has_results,
    )


def load_top_bottom_tickers(
    output_dir: Optional[str] = None,
    top_n: int = 5,
    bottom_n: int = 5,
) -> TopBottomTickers:
    """
    Load top/bottom tickers from output directory.

    Args:
        output_dir: Path to output directory
        top_n: Number of top tickers
        bottom_n: Number of bottom tickers

    Returns:
        Dict with 'top' and 'bottom' ticker lists
    """
    store = ResultStore(output_dir or DEFAULT_OUTPUT_DIR)
    latest_run = store.get_latest_run()
    ticker_stats_path = str(latest_run.ticker_stats_path) if latest_run and latest_run.ticker_stats_path else ""
    raw = get_top_bottom_tickers(ticker_stats_path, top_n=top_n, bottom_n=bottom_n)
    return TopBottomTickers(
        top=_normalize_ticker_stats(raw.get("top", [])),
        bottom=_normalize_ticker_stats(raw.get("bottom", [])),
    )


@router.post("/run", response_model=BacktestResponse)
def run_backtest(request: BacktestRequest):
    """Run a backtest with the specified date range."""
    result = run_backtest_task(request.start_date, request.end_date)
    return BacktestResponse(**result)


@router.get("/results", response_model=BacktestArtifactsResponse)
def get_results():
    """Get backtest results (trade log and ticker stats)."""
    return load_results()


@router.get("/tickers", response_model=TopBottomTickers)
def get_tickers():
    """Get top 5 and bottom 5 tickers by P&L."""
    return load_top_bottom_tickers()


@router.get("/list", response_model=BacktestListResponse)
def list_backtests():
    """List all available backtest results."""
    backtests = list_available_backtests(DEFAULT_OUTPUT_DIR)
    return BacktestListResponse(backtests=[BacktestMetadata(**backtest) for backtest in backtests])


@router.get("/latest", response_model=BacktestResults)
def get_latest_results(range: Optional[str] = None) -> BacktestResults:
    """Get the latest backtest results or a range-specific backtest.

    Query parameters:
    - range: optional selector used to choose a backtest run. Supports exact
      directory name, exact timestamp, exact period string ("YYYY-MM-DD to
      YYYY-MM-DD"), or a four-digit year prefix. Special value 'ALL' returns
      the latest run.
    """
    store = _get_store_or_404(DEFAULT_OUTPUT_DIR)
    try:
        chosen = _resolve_requested_run(store, range)
        return _get_backtest_results_by_dir(str(chosen.result_dir), chosen.dir_name, run=chosen)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{timestamp}", response_model=BacktestResults)
def get_results_by_timestamp(timestamp: str) -> BacktestResults:
    """Get backtest results for a specific timestamp."""
    store = ResultStore(DEFAULT_OUTPUT_DIR)
    try:
        matched = store.get_run_by_timestamp(timestamp)
        if matched is None:
            raise HTTPException(status_code=404, detail=f"No backtest results found for timestamp: {timestamp}")
        return _get_backtest_results_by_dir(str(matched.result_dir), matched.dir_name, run=matched)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get results for timestamp {timestamp}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _build_run_metadata(run) -> BacktestRunInfo | None:
    if run is None:
        return None
    return BacktestRunInfo(
        run_id=getattr(run, "dir_name", ""),
        run_label=getattr(run, "run_label", None),
        experiment_name=getattr(run, "experiment_name", None),
        strategy_name=getattr(run, "strategy_name", None),
        benchmark_enabled=getattr(run, "benchmark_enabled", None),
        rule_profile=getattr(run, "rule_profile", None),
        tags=getattr(run, "tags", None) or [],
    )


def _load_run_manifest(result_dir: str) -> dict:
    manifest_path = Path(result_dir) / "run_manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        logger.warning(f"Failed to load run manifest from {manifest_path}: {exc}")
        return {}


def _build_visualization(result_dir: str, trades: list[TradeRecord]) -> BacktestVisualization:
    manifest = _load_run_manifest(result_dir)
    metrics = manifest.get("metrics", {}) if isinstance(manifest.get("metrics"), dict) else {}
    initial_capital = metrics.get("initial_capital")
    final_capital = metrics.get("final_capital")
    total_pnl = metrics.get("total_pnl", 0)

    if initial_capital is None and final_capital is not None:
        try:
            initial_capital = float(final_capital) - float(total_pnl or 0)
        except (TypeError, ValueError):
            initial_capital = None

    trade_log_path = Path(result_dir) / "trade_log.csv"
    raw_events: list[dict] = []
    if trade_log_path.exists():
        raw_events = load_trade_log(str(trade_log_path))

    if not raw_events:
        for trade in trades:
            if trade.entry_date and trade.entry_price is not None:
                raw_events.append(
                    {
                        "date": trade.entry_date,
                        "action": "ENTRY",
                        "ticker": trade.ticker,
                        "price": trade.entry_price,
                        "pnl": 0,
                    }
                )
            if trade.exit_date and trade.exit_price is not None:
                raw_events.append(
                    {
                        "date": trade.exit_date,
                        "action": "EXIT",
                        "ticker": trade.ticker,
                        "price": trade.exit_price,
                        "pnl": trade.pnl or 0,
                    }
                )

    if not raw_events:
        return BacktestVisualization()

    events_df = pd.DataFrame(raw_events)
    if events_df.empty or "date" not in events_df.columns:
        return BacktestVisualization()

    events_df["date"] = pd.to_datetime(events_df["date"], errors="coerce")
    events_df = events_df.dropna(subset=["date"]).sort_values(["date", "ticker", "action"])
    if events_df.empty:
        return BacktestVisualization()

    events_df["time"] = events_df["date"].dt.strftime("%Y-%m-%d")
    events_df["pnl"] = pd.to_numeric(events_df.get("pnl"), errors="coerce").fillna(0.0)
    events_df["price"] = pd.to_numeric(events_df.get("price"), errors="coerce")

    signal_events = [
        SignalEventPoint(
            time=row.time,
            action=str(row.action or ""),
            signal=1 if str(row.action).upper() == "ENTRY" else -1 if str(row.action).upper() == "EXIT" else 0,
            ticker=str(row.ticker or ""),
            price=float(row.price) if not pd.isna(row.price) else 0.0,
            pnl=float(row.pnl) if not pd.isna(row.pnl) else None,
            label=f"{str(row.action or '').upper()} {str(row.ticker or '').upper()}".strip(),
        )
        for row in events_df.itertuples(index=False)
    ]

    base_equity = float(initial_capital or 0.0)
    daily_realized_pnl = events_df.groupby("time", sort=True)["pnl"].sum()
    equity_curve: list[TimeSeriesPoint] = []
    current_equity = base_equity
    for time, pnl in daily_realized_pnl.items():
        current_equity += float(pnl)
        equity_curve.append(TimeSeriesPoint(time=time, value=current_equity))

    if not equity_curve and final_capital is not None:
        last_time = events_df["time"].iloc[-1]
        equity_curve.append(TimeSeriesPoint(time=last_time, value=float(final_capital)))

    rolling_peak = None
    drawdown: list[TimeSeriesPoint] = []
    for point in equity_curve:
        rolling_peak = point.value if rolling_peak is None else max(rolling_peak, point.value)
        drawdown_value = 0.0 if not rolling_peak else (point.value / rolling_peak) - 1
        drawdown.append(TimeSeriesPoint(time=point.time, value=drawdown_value))

    return BacktestVisualization(
        equity_curve=equity_curve,
        drawdown=drawdown,
        signal_events=signal_events,
    )


def _get_backtest_results_by_dir(result_dir: str, dir_name: str, run=None) -> BacktestResults:
    """Helper function to load backtest results from a directory."""
    if not os.path.exists(result_dir):
        raise HTTPException(status_code=404, detail=f"Backtest directory not found: {dir_name}")

    if run is None:
        run = ResultStore(DEFAULT_OUTPUT_DIR).get_run_by_timestamp(dir_name)
    
    # Load summary metrics
    summary = BacktestSummary(**load_backtest_summary(result_dir))
    
    # Load trade data
    # Some backtests generate 'trades.csv' while others use 'trade_log.csv'. Try both.
    trades = []
    trade_log_path = None
    trades_candidates = [
        os.path.join(result_dir, "trades.csv"),
        os.path.join(result_dir, "trade_log.csv"),
    ]
    for p in trades_candidates:
        if os.path.exists(p):
            trades = _normalize_trade_records(load_trade_log(p))
            trade_log_path = p
            break

    # Load ticker statistics
    ticker_stats_path = os.path.join(result_dir, "ticker_stats.csv")
    ticker_stats = _normalize_ticker_stats(load_ticker_stats(ticker_stats_path))

    # Load charts as base64
    charts = {}
    charts_dir = os.path.join(result_dir, "charts")
    if os.path.exists(charts_dir):
        for chart_file in sorted(os.listdir(charts_dir)):
            if chart_file.endswith(".png"):
                chart_path = os.path.join(charts_dir, chart_file)
                chart_key = chart_file.replace(".png", "")
                charts[chart_key] = get_chart_as_base64(chart_path)

    # Also include any top-level PNGs in the result_dir (e.g. equity_curve.png, drawdown.png)
    try:
        for root_file in sorted(os.listdir(result_dir)):
            if root_file.endswith('.png'):
                root_path = os.path.join(result_dir, root_file)
                root_key = root_file.replace('.png', '')
                if root_key not in charts:
                    charts[root_key] = get_chart_as_base64(root_path)
    except Exception:
        pass

    # If no per-ticker charts were found (only top-level summary images), attempt to generate them
    need_generation = True
    # Detect existing per-ticker charts by key patterns
    if charts:
        for k in charts.keys():
            if k.startswith('top_') or k.startswith('bottom_') or k.endswith('_price_chart'):
                need_generation = False
                break

    if need_generation:
        # Ensure repo root is on sys.path so sibling 'python' package can be imported
        import sys
        from pathlib import Path as _Path
        _repo_root = str(_Path(__file__).resolve().parents[2])
        if _repo_root not in sys.path:
            sys.path.insert(0, _repo_root)
        # First try the full-featured ticker_charts module which may fetch data (yfinance)
        try:
            # Import here to avoid hard dependency unless needed
            from python.backtest import ticker_charts as tc
            # Only attempt generation if ticker_stats exists (we have tickers to create charts for)
            if os.path.exists(ticker_stats_path):
                logger.info("No per-ticker charts found; attempting to generate per-ticker charts")
                try:
                    # generate_top_bottom_charts will fetch price data as needed and write PNGs under result_dir/charts
                    tc.generate_top_bottom_charts(ticker_stats_path, trade_log_path or "", result_dir)
                    # Reload generated charts
                    if os.path.exists(charts_dir):
                        for chart_file in sorted(os.listdir(charts_dir)):
                            if chart_file.endswith(".png"):
                                chart_path = os.path.join(charts_dir, chart_file)
                                chart_key = chart_file.replace(".png", "")
                                charts[chart_key] = get_chart_as_base64(chart_path)
                except Exception as inner_e:
                    logger.warning(f"Chart generation attempted but failed: {inner_e}")
                    # Attempt lightweight placeholder generation as a fallback (no network dependency)
                    try:
                        logger.info("Attempting placeholder chart generation as fallback")
                        generate_placeholder_charts(result_dir, ticker_stats_path, trade_log_path or "")
                        if os.path.exists(charts_dir):
                            for chart_file in sorted(os.listdir(charts_dir)):
                                if chart_file.endswith(".png"):
                                    chart_path = os.path.join(charts_dir, chart_file)
                                    chart_key = chart_file.replace(".png", "")
                                    charts[chart_key] = get_chart_as_base64(chart_path)
                    except Exception as fallback_e:
                        logger.error(f"Placeholder chart generation failed: {fallback_e}")
        except Exception as e:
            logger.debug(f"Ticker chart generation module not available: {e}")
            # If the heavy chart module isn't available, try the lightweight placeholder generator
            try:
                logger.info("Ticker chart module not available; generating placeholder charts")
                generate_placeholder_charts(result_dir, ticker_stats_path or "", trade_log_path or "")
                if os.path.exists(charts_dir):
                    for chart_file in sorted(os.listdir(charts_dir)):
                        if chart_file.endswith(".png"):
                            chart_path = os.path.join(charts_dir, chart_file)
                            chart_key = chart_file.replace(".png", "")
                            charts[chart_key] = get_chart_as_base64(chart_path)
            except Exception as fallback_e:
                logger.error(f"Placeholder chart generation failed: {fallback_e}")

    # Provide convenient aliases: map filenames to ticker-based keys so frontend can find images by ticker symbol
    try:
        for chart_key in list(charts.keys()):
            try:
                symbol = None
                if chart_key.endswith('_price_chart'):
                    symbol = chart_key.replace('_price_chart', '')
                else:
                    parts = chart_key.split('_')
                    if len(parts) >= 2:
                        cand = parts[-1]
                        if any(ch.isalpha() for ch in cand):
                            symbol = cand
                if symbol:
                    if f"{symbol}_price_chart" not in charts:
                        charts[f"{symbol}_price_chart"] = charts[chart_key]
                    if symbol not in charts:
                        charts[symbol] = charts[chart_key]
            except Exception:
                continue
    except Exception:
        pass

    return BacktestResults(
        timestamp=dir_name,
        summary=summary,
        trades=trades,
        ticker_stats=ticker_stats,
        charts=charts,
        run_metadata=_build_run_metadata(run),
        visualization=_build_visualization(result_dir, trades),
    )


@router.get('/ohlc', response_model=OhlcResponse)
def get_ohlc(ticker: str, range: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Return OHLCV data for a given ticker and date range.

    Query params:
    - ticker: required ticker symbol
    - range: optional year string (e.g., '2023') or 'ALL'
    - start_date, end_date: optional explicit dates (YYYY-MM-DD)

    Returns JSON: { data: [{ time: 'YYYY-MM-DD', open, high, low, close, volume }, ...] }
    """
    # Determine date range
    if range and not (start_date and end_date):
        r = range.strip()
        if r.upper() == 'ALL':
            # default to last 365 days
            from datetime import datetime, timedelta
            end = datetime.utcnow().date()
            start = end - timedelta(days=365)
            start_date = start.isoformat()
            end_date = end.isoformat()
        elif len(r) == 4 and r.isdigit():
            start_date = f"{r}-01-01"
            end_date = f"{r}-12-31"
        else:
            # unknown range, fallback to last 365 days
            from datetime import datetime, timedelta
            end = datetime.utcnow().date()
            start = end - timedelta(days=365)
            start_date = start.isoformat()
            end_date = end.isoformat()

    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail='start_date and end_date or range (year) must be provided')

    # Use python.backtest.ticker_charts to fetch via yfinance when available
    try:
        # Import ticker_charts by file path to avoid executing python.backtest __init__ which pulls other modules
        import importlib.util
        from pathlib import Path as _Path
        _repo_root = str(_Path(__file__).resolve().parents[2])
        tc_path = os.path.join(_repo_root, 'python', 'backtest', 'ticker_charts.py')
        spec = importlib.util.spec_from_file_location('ticker_charts_module', tc_path)
        tc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tc)

        if not getattr(tc, 'YFINANCE_AVAILABLE', False):
            raise RuntimeError('yfinance not available in environment')

        # fetch via yfinance inside the ticker_charts module
        stock = tc.yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        if df is None or df.empty:
            return OhlcResponse()

        # normalize index and columns
        df.reset_index(inplace=True)
        # Determine date column name if different
        date_col = 'Date' if 'Date' in df.columns else df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')

        data = []
        for _, row in df.iterrows():
            data.append({
                'time': row[date_col],
                'open': None if pd.isna(row.get('Open')) else float(row.get('Open')),
                'high': None if pd.isna(row.get('High')) else float(row.get('High')),
                'low': None if pd.isna(row.get('Low')) else float(row.get('Low')),
                'close': None if pd.isna(row.get('Close')) else float(row.get('Close')),
                'volume': None if pd.isna(row.get('Volume')) else int(row.get('Volume')),
            })
        return OhlcResponse(data=[OhlcPoint(**item) for item in data])
    except Exception as e:
        logger.error(f'Failed to fetch OHLC for {ticker}: {e}')
        raise HTTPException(status_code=503, detail=str(e))
