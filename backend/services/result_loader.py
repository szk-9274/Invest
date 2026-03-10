"""
Result Loader Service

Loads backtest results from CSV files (trade_log.csv, ticker_stats.csv)
and provides data access for the API layer.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from services.result_store import ResultStore


def load_trade_log(csv_path: str) -> List[Dict]:
    """
    Load trade log from CSV file.

    Args:
        csv_path: Path to trade_log.csv

    Returns:
        List of trade records as dictionaries
    """
    if not os.path.exists(csv_path):
        # Attempt to find the file in the latest available backtest directory under the same output root
        def _find_latest_csv_in_sibling_backtests(missing_path, filename):
            parent = os.path.dirname(missing_path)
            output_root = os.path.dirname(parent)
            if not os.path.exists(output_root):
                return None
            for d in sorted(os.listdir(output_root), reverse=True):
                candidate_dir = os.path.join(output_root, d)
                if not os.path.isdir(candidate_dir):
                    continue
                candidate = os.path.join(candidate_dir, filename)
                if os.path.exists(candidate):
                    return candidate
            return None

        found = _find_latest_csv_in_sibling_backtests(csv_path, os.path.basename(csv_path))
        if found:
            logger.info(f"Trade log not found at {csv_path}, falling back to latest: {found}")
            csv_path = found
        else:
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
        # Try to locate ticker_stats in the latest backtest sibling directories
        def _find_latest_csv_in_sibling_backtests(missing_path, filename):
            parent = os.path.dirname(missing_path)
            output_root = os.path.dirname(parent)
            if not os.path.exists(output_root):
                return None
            for d in sorted(os.listdir(output_root), reverse=True):
                candidate_dir = os.path.join(output_root, d)
                if not os.path.isdir(candidate_dir):
                    continue
                candidate = os.path.join(candidate_dir, filename)
                if os.path.exists(candidate):
                    return candidate
            return None

        found = _find_latest_csv_in_sibling_backtests(csv_path, os.path.basename(csv_path))
        if found:
            logger.info(f"Ticker stats not found at {csv_path}, falling back to latest: {found}")
            csv_path = found
        else:
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
        # Try to locate trade_log in sibling backtest directories under the same output root
        def _find_latest_csv_in_sibling_backtests(missing_path, filename):
            parent = os.path.dirname(missing_path)
            output_root = os.path.dirname(parent)
            if not os.path.exists(output_root):
                return None
            for d in sorted(os.listdir(output_root), reverse=True):
                candidate_dir = os.path.join(output_root, d)
                if not os.path.isdir(candidate_dir):
                    continue
                candidate = os.path.join(candidate_dir, filename)
                if os.path.exists(candidate):
                    return candidate
            return None

        found = _find_latest_csv_in_sibling_backtests(csv_path, os.path.basename(csv_path))
        if found:
            logger.info(f"Trade log not found at {csv_path}, falling back to latest: {found}")
            csv_path = found
        else:
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


def get_chart_as_base64(chart_path: str) -> Optional[str]:
    """
    Convert chart image to base64 string.

    Args:
        chart_path: Path to chart image file

    Returns:
        Base64 encoded string or None if file not found
    """
    import base64

    if not os.path.exists(chart_path):
        logger.warning(f"Chart not found: {chart_path}")
        return None

    try:
        with open(chart_path, "rb") as f:
            image_data = f.read()
            base64_string = base64.b64encode(image_data).decode("utf-8")
            return f"data:image/png;base64,{base64_string}"
    except Exception as e:
        logger.error(f"Failed to encode chart as base64: {e}")
        return None


def list_available_backtests(output_dir: str) -> List[Dict]:
    """
    List all available backtest results with metadata.

    Args:
        output_dir: Path to backtest output directory

    Returns:
        List of backtest metadata dictionaries
    """
    return ResultStore(output_dir).list_backtests()


def load_backtest_summary(output_dir: str) -> Dict:
    """
    Load backtest summary metrics from CSV files.

    Args:
        output_dir: Path to specific backtest output directory

    Returns:
        Dictionary with summary metrics
    """
    if not os.path.exists(output_dir):
        return {}

    summary = {}
    try:
        manifest_path = os.path.join(output_dir, "run_manifest.json")
        if os.path.exists(manifest_path):
            manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
            metrics = manifest.get("metrics", {})
            if metrics:
                information_ratio = metrics.get("information_ratio")
                if information_ratio is None:
                    information_ratio = metrics.get("sharpe_ratio") or 0
                return {
                    "total_trades": metrics.get("total_trades", 0),
                    "winning_trades": metrics.get("winning_trades", 0),
                    "losing_trades": metrics.get("losing_trades", 0),
                    "win_rate": metrics.get("win_rate", 0),
                    "total_pnl": metrics.get("total_pnl", 0),
                    "avg_win": metrics.get("avg_win", 0),
                    "avg_loss": metrics.get("avg_loss", 0),
                    "final_capital": metrics.get("final_capital", 0),
                    "total_return_pct": metrics.get("total_return_pct", 0),
                    "annual_return_pct": metrics.get("annual_return_pct", 0),
                    "information_ratio": information_ratio,
                    "max_drawdown_pct": metrics.get("max_drawdown_pct", 0),
                    "sharpe_ratio": metrics.get("sharpe_ratio", 0),
                }

        # Load trades.csv for gross statistics
        trades_path = os.path.join(output_dir, "trades.csv")
        if os.path.exists(trades_path):
            df = pd.read_csv(trades_path)
            if not df.empty:
                # Calculate metrics
                total_pnl = float(df["pnl"].sum())
                winning_trades = len(df[df["pnl"] > 0])
                losing_trades = len(df[df["pnl"] <= 0])
                total_trades = len(df)

                summary["total_trades"] = total_trades
                summary["winning_trades"] = winning_trades
                summary["losing_trades"] = losing_trades
                summary["win_rate"] = winning_trades / total_trades if total_trades > 0 else 0
                summary["total_pnl"] = total_pnl
                summary["avg_win"] = float(df[df["pnl"] > 0]["pnl"].mean()) if winning_trades > 0 else 0
                summary["avg_loss"] = float(df[df["pnl"] <= 0]["pnl"].mean()) if losing_trades > 0 else 0

        return summary
    except Exception as e:
        logger.error(f"Failed to load backtest summary: {e}")
        return {}


def generate_placeholder_charts(
    result_dir: str,
    ticker_stats_path: str,
    trade_log_path: str,
    top_n: int = 5,
    bottom_n: int = 5,
) -> List[str]:
    """
    Generate simple placeholder PNG charts for top/bottom tickers without external data.

    This is a lightweight fallback used when yfinance/mplfinance are unavailable
    or when network access fails. The generated images are simple dark-themed
    thumbnails containing the ticker symbol and entry/exit markers derived from
    the trade_log (if available).

    Args:
        result_dir: Backtest result directory where charts/ will be created
        ticker_stats_path: Path to ticker_stats.csv
        trade_log_path: Path to trade_log.csv (may be empty)
        top_n: number of top tickers
        bottom_n: number of bottom tickers

    Returns:
        List of file paths to generated images
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except Exception:
        logger.error("matplotlib not available for placeholder chart generation")
        return []

    charts_dir = os.path.join(result_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # Load ticker list
    try:
        if not os.path.exists(ticker_stats_path):
            logger.warning(f"Ticker stats not found for placeholder generation: {ticker_stats_path}")
            return []
        stats_df = pd.read_csv(ticker_stats_path)
        if stats_df.empty:
            return []
        stats_df = stats_df.sort_values('total_pnl', ascending=False)
        top = stats_df.head(min(top_n, len(stats_df)))['ticker'].tolist()
        bottom = stats_df.tail(min(bottom_n, len(stats_df)))['ticker'].tolist()
    except Exception as e:
        logger.error(f"Failed to read ticker stats for placeholder generation: {e}")
        return []

    # Load trades if available
    trades_df = None
    if trade_log_path and os.path.exists(trade_log_path):
        try:
            trades_df = pd.read_csv(trade_log_path)
            if not trades_df.empty:
                trades_df['date'] = pd.to_datetime(trades_df['date'])
        except Exception:
            trades_df = None

    generated = []

    def _make_thumb(ticker: str, prefix: str, idx: int):
        try:
            fig, ax = plt.subplots(figsize=(6, 3), facecolor='#0b2948')
            ax.set_facecolor('#0b2948')
            # Title
            ax.text(0.5, 0.75, ticker, color='white', fontsize=18, ha='center', va='center', transform=ax.transAxes)

            if trades_df is not None and not trades_df.empty:
                td = trades_df[trades_df['ticker'] == ticker].sort_values('date')
                if not td.empty:
                    xs = range(len(td))
                    ys = td['price'].fillna(1.0)
                    colors = ['green' if a == 'ENTRY' else 'red' for a in td.get('action', ['ENTRY'] * len(td))]
                    ax.scatter(xs, ys, c=colors, edgecolors='white')
                    ax.set_ylim(ys.min() * 0.9, ys.max() * 1.1)
            ax.axis('off')
            filename = f"{prefix}_{idx:02d}_{ticker}.png"
            path = os.path.join(charts_dir, filename)
            fig.savefig(path, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            generated.append(path)
        except Exception as e:
            logger.error(f"Failed to create placeholder for {ticker}: {e}")

    for i, t in enumerate(top, start=1):
        _make_thumb(t, 'top', i)
    for i, t in enumerate(bottom, start=1):
        _make_thumb(t, 'bottom', i)

    return generated
