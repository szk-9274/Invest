"""
Backtest API Endpoints

Provides REST API for:
- Running backtests
- Retrieving results
- Getting top/bottom tickers
"""
import os
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from services.result_loader import (
    load_trade_log,
    load_ticker_stats,
    get_top_bottom_tickers,
)

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
    # In a full implementation, this would invoke the backtest engine
    # For now, return a placeholder response
    return {"status": "started", "message": f"Backtest started for {start_date} to {end_date}"}


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
