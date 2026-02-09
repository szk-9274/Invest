"""
Result Loader Service

Loads backtest results from CSV files (trade_log.csv, ticker_stats.csv)
and provides data access for the API layer.
"""
import os
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger


def load_trade_log(csv_path: str) -> List[Dict]:
    """
    Load trade log from CSV file.

    Args:
        csv_path: Path to trade_log.csv

    Returns:
        List of trade records as dictionaries
    """
    if not os.path.exists(csv_path):
        logger.warning(f"Trade log not found: {csv_path}")
        return []

    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return []
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Failed to load trade log: {e}")
        return []


def load_ticker_stats(csv_path: str) -> List[Dict]:
    """
    Load ticker statistics from CSV file.

    Args:
        csv_path: Path to ticker_stats.csv

    Returns:
        List of ticker stat records as dictionaries
    """
    if not os.path.exists(csv_path):
        logger.warning(f"Ticker stats not found: {csv_path}")
        return []

    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return []
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Failed to load ticker stats: {e}")
        return []


def get_top_bottom_tickers(
    csv_path: str,
    top_n: int = 5,
    bottom_n: int = 5,
) -> Dict[str, List[Dict]]:
    """
    Extract top N winners and bottom N losers from ticker_stats.csv.

    Args:
        csv_path: Path to ticker_stats.csv
        top_n: Number of top tickers to return
        bottom_n: Number of bottom tickers to return

    Returns:
        Dict with 'top' and 'bottom' lists of ticker records
    """
    if not os.path.exists(csv_path):
        logger.warning(f"Ticker stats not found: {csv_path}")
        return {"top": [], "bottom": []}

    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return {"top": [], "bottom": []}

        # Sort by total_pnl descending
        df_sorted = df.sort_values("total_pnl", ascending=False)

        # Top N winners
        top_df = df_sorted.head(min(top_n, len(df_sorted)))
        top_records = top_df.to_dict(orient="records")

        # Bottom N losers (sorted ascending for bottom)
        bottom_df = df_sorted.tail(min(bottom_n, len(df_sorted)))
        # Re-sort ascending for the bottom list
        bottom_df = bottom_df.sort_values("total_pnl", ascending=True)
        bottom_records = bottom_df.to_dict(orient="records")

        return {"top": top_records, "bottom": bottom_records}

    except Exception as e:
        logger.error(f"Failed to load ticker stats for top/bottom: {e}")
        return {"top": [], "bottom": []}


def get_enriched_trade_markers(
    csv_path: str,
    ticker: str,
) -> Dict[str, List[Dict]]:
    """
    Get enriched trade markers with tooltip data for a specific ticker.

    Each exit marker includes:
    - date: Exit date
    - price: Exit price
    - pnl: Profit/Loss
    - holding_days: Number of days from entry to exit
    - entry_date: Corresponding entry date
    - entry_price: Corresponding entry price

    Args:
        csv_path: Path to trade_log.csv
        ticker: Ticker symbol to filter

    Returns:
        Dict with 'entries' and 'exits' lists
    """
    if not os.path.exists(csv_path):
        logger.warning(f"Trade log not found: {csv_path}")
        return {"entries": [], "exits": []}

    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return {"entries": [], "exits": []}

        # Filter by ticker
        ticker_trades = df[df["ticker"] == ticker].copy()
        if ticker_trades.empty:
            return {"entries": [], "exits": []}

        # Convert dates
        ticker_trades["date"] = pd.to_datetime(ticker_trades["date"])

        # Separate entries and exits
        entries_df = ticker_trades[ticker_trades["action"] == "ENTRY"].reset_index(
            drop=True
        )
        exits_df = ticker_trades[ticker_trades["action"] == "EXIT"].reset_index(
            drop=True
        )

        # Build entry markers
        entries = []
        for _, row in entries_df.iterrows():
            entries.append(
                {
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "price": float(row["price"]),
                }
            )

        # Build exit markers with enriched data
        # Pair each exit with its corresponding entry (by order)
        exits = []
        for i, (_, row) in enumerate(exits_df.iterrows()):
            exit_marker = {
                "date": row["date"].strftime("%Y-%m-%d"),
                "price": float(row["price"]),
                "pnl": float(row.get("pnl", 0)),
            }

            # Match with corresponding entry (by index)
            if i < len(entries_df):
                entry_row = entries_df.iloc[i]
                entry_date = entry_row["date"]
                exit_date = row["date"]
                holding_days = (exit_date - entry_date).days

                exit_marker["holding_days"] = int(holding_days)
                exit_marker["entry_date"] = entry_date.strftime("%Y-%m-%d")
                exit_marker["entry_price"] = float(entry_row["price"])
            else:
                exit_marker["holding_days"] = 0
                exit_marker["entry_date"] = ""
                exit_marker["entry_price"] = 0.0

            exits.append(exit_marker)

        return {"entries": entries, "exits": exits}

    except Exception as e:
        logger.error(f"Failed to load enriched trade markers: {e}")
        return {"entries": [], "exits": []}
