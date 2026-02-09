"""
Charts API Endpoints

Provides REST API for:
- Getting OHLCV chart data for a ticker
- Getting trade markers for a ticker
"""
import os
from typing import Dict, List, Optional

from fastapi import APIRouter, Query
from loguru import logger

from services.result_loader import load_trade_log

router = APIRouter(prefix="/api/charts", tags=["charts"])

# Default paths
DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "python",
    "output",
    "backtest",
)


def get_chart_data(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict:
    """
    Get OHLCV chart data for a ticker.

    In a full implementation, this would fetch data from yfinance or cache.
    For now, returns a placeholder structure.

    Args:
        ticker: Stock ticker symbol
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        Dict with ticker, dates, OHLCV arrays, and indicator arrays
    """
    logger.info(f"Chart data requested for {ticker} ({start_date} to {end_date})")

    # Placeholder - in production, fetch from yfinance or cache
    return {
        "ticker": ticker,
        "dates": [],
        "open": [],
        "high": [],
        "low": [],
        "close": [],
        "volume": [],
        "sma20": [],
        "sma50": [],
        "sma200": [],
    }


def get_trade_markers(
    ticker: str,
    output_dir: Optional[str] = None,
) -> Dict:
    """
    Get trade entry/exit markers for a ticker from trade_log.csv.

    Args:
        ticker: Stock ticker symbol
        output_dir: Path to output directory

    Returns:
        Dict with 'entries' and 'exits' lists
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    trade_log_path = os.path.join(output_dir, "trade_log.csv")
    all_trades = load_trade_log(trade_log_path)

    entries = []
    exits = []

    for trade in all_trades:
        if trade.get("ticker") != ticker:
            continue

        if trade.get("action") == "ENTRY":
            entries.append({
                "date": trade.get("date"),
                "price": trade.get("price"),
            })
        elif trade.get("action") == "EXIT":
            exits.append({
                "date": trade.get("date"),
                "price": trade.get("price"),
                "pnl": trade.get("pnl", 0),
            })

    return {"entries": entries, "exits": exits}


@router.get("/{ticker}")
def get_ticker_chart(
    ticker: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    """Get OHLCV chart data for a specific ticker."""
    return get_chart_data(ticker, start_date=start_date, end_date=end_date)


@router.get("/{ticker}/trades")
def get_ticker_trades(ticker: str):
    """Get trade entry/exit markers for a specific ticker."""
    return get_trade_markers(ticker)
