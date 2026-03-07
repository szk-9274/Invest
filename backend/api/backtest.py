"""
Backtest API Endpoints

Provides REST API for:
- Running backtests
- Retrieving results
- Getting top/bottom tickers
"""
import os
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

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

router = APIRouter(prefix="/api/backtest", tags=["backtest"])

# Default paths for result files
DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "python",
    "output",
    "backtest",
)


class BacktestRequest(BaseModel):
    """Request model for backtest execution."""

    start_date: str
    end_date: str


class BacktestResponse(BaseModel):
    """Response model for backtest execution."""

    status: str
    message: str
    job_id: Optional[str] = None


class BacktestResultsResponse(BaseModel):
    """Response model for backtest results."""

    timestamp: str
    summary: Dict
    trades: List[Dict]
    ticker_stats: List[Dict]
    charts: Dict[str, Optional[str]]  # chart_name -> base64_image


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


def load_results(output_dir: Optional[str] = None) -> Dict:
    """
    Load backtest results from output directory.

    Args:
        output_dir: Path to output directory (defaults to DEFAULT_OUTPUT_DIR)

    Returns:
        Dict with trade_log, ticker_stats, and has_results flag
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    trade_log_path = os.path.join(output_dir, "trade_log.csv")
    ticker_stats_path = os.path.join(output_dir, "ticker_stats.csv")

    # If files are not present directly under output_dir, try the latest
    # backtest_* subdirectory (this matches how backtests are saved).
    if not (os.path.exists(trade_log_path) or os.path.exists(ticker_stats_path)):
        try:
            dirs = sorted([d for d in os.listdir(output_dir) if d.startswith("backtest_")], reverse=True)
            if dirs:
                latest = dirs[0]
                trade_log_path = os.path.join(output_dir, latest, "trade_log.csv")
                ticker_stats_path = os.path.join(output_dir, latest, "ticker_stats.csv")
        except Exception:
            # Fall back to original paths if anything goes wrong
            pass

    trade_log = load_trade_log(trade_log_path)
    ticker_stats = load_ticker_stats(ticker_stats_path)

    has_results = len(trade_log) > 0 or len(ticker_stats) > 0

    return {
        "trade_log": trade_log,
        "ticker_stats": ticker_stats,
        "has_results": has_results,
    }


def load_top_bottom_tickers(
    output_dir: Optional[str] = None,
    top_n: int = 5,
    bottom_n: int = 5,
) -> Dict:
    """
    Load top/bottom tickers from output directory.

    Args:
        output_dir: Path to output directory
        top_n: Number of top tickers
        bottom_n: Number of bottom tickers

    Returns:
        Dict with 'top' and 'bottom' ticker lists
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    ticker_stats_path = os.path.join(output_dir, "ticker_stats.csv")

    # If no root ticker_stats, fall back to latest backtest directory
    if not os.path.exists(ticker_stats_path):
        try:
            dirs = sorted([d for d in os.listdir(output_dir) if d.startswith("backtest_")], reverse=True)
            if dirs:
                latest = dirs[0]
                ticker_stats_path = os.path.join(output_dir, latest, "ticker_stats.csv")
        except Exception:
            pass

    return get_top_bottom_tickers(ticker_stats_path, top_n=top_n, bottom_n=bottom_n)


@router.post("/run", response_model=BacktestResponse)
def run_backtest(request: BacktestRequest):
    """Run a backtest with the specified date range."""
    result = run_backtest_task(request.start_date, request.end_date)
    return BacktestResponse(**result)


@router.get("/results")
def get_results():
    """Get backtest results (trade log and ticker stats)."""
    return load_results()


@router.get("/tickers")
def get_tickers():
    """Get top 5 and bottom 5 tickers by P&L."""
    return load_top_bottom_tickers()


@router.get("/list")
def list_backtests():
    """List all available backtest results."""
    output_dir = DEFAULT_OUTPUT_DIR
    backtests = list_available_backtests(output_dir)
    return {"backtests": backtests}


@router.get("/latest")
def get_latest_results() -> BacktestResultsResponse:
    """Get the latest backtest results."""
    output_dir = DEFAULT_OUTPUT_DIR
    
    # Find the latest backtest directory
    if not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail="No backtest results found")
    
    try:
        dirs = sorted([d for d in os.listdir(output_dir) if d.startswith("backtest_")], reverse=True)
        if not dirs:
            raise HTTPException(status_code=404, detail="No backtest results found")
        
        latest_dir = dirs[0]
        return _get_backtest_results_by_dir(os.path.join(output_dir, latest_dir), latest_dir)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{timestamp}")
def get_results_by_timestamp(timestamp: str) -> BacktestResultsResponse:
    """Get backtest results for a specific timestamp."""
    output_dir = DEFAULT_OUTPUT_DIR
    
    # Find directory matching timestamp pattern
    try:
        matching_dirs = [d for d in os.listdir(output_dir) if timestamp in d]
        if not matching_dirs:
            raise HTTPException(status_code=404, detail=f"No backtest results found for timestamp: {timestamp}")
        
        dir_name = matching_dirs[0]
        return _get_backtest_results_by_dir(os.path.join(output_dir, dir_name), dir_name)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get results for timestamp {timestamp}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_backtest_results_by_dir(result_dir: str, dir_name: str) -> BacktestResultsResponse:
    """Helper function to load backtest results from a directory."""
    if not os.path.exists(result_dir):
        raise HTTPException(status_code=404, detail=f"Backtest directory not found: {dir_name}")
    
    # Load summary metrics
    summary = load_backtest_summary(result_dir)
    
    # Load trade data
    # Some backtests generate 'trades.csv' while others use 'trade_log.csv'. Try both.
    trades = []
    trade_log_path = None
    trades_candidates = [
        os.path.join(result_dir, "trades.csv"),
        os.path.join(result_dir, "trade_log.csv"),
        os.path.join(result_dir, "trade_log.csv"),
    ]
    for p in trades_candidates:
        if os.path.exists(p):
            trades = load_trade_log(p)
            trade_log_path = p
            break

    # Load ticker statistics
    ticker_stats_path = os.path.join(result_dir, "ticker_stats.csv")
    ticker_stats = load_ticker_stats(ticker_stats_path)

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
                generate_placeholder_charts(result_dir, ticker_stats_path, trade_log_path or "")
                if os.path.exists(charts_dir):
                    for chart_file in sorted(os.listdir(charts_dir)):
                        if chart_file.endswith(".png"):
                            chart_path = os.path.join(charts_dir, chart_file)
                            chart_key = chart_file.replace(".png", "")
                            charts[chart_key] = get_chart_as_base64(chart_path)
            except Exception as fallback_e:
                logger.error(f"Placeholder chart generation failed: {fallback_e}")
    
    return BacktestResultsResponse(
        timestamp=dir_name,
        summary=summary,
        trades=trades,
        ticker_stats=ticker_stats,
        charts=charts,
    )
