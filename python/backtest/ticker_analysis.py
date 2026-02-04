"""
Ticker Analysis Module

Aggregates EXIT trades by ticker to compute:
- Total P&L per ticker
- Trade count per ticker
- Top N winners and bottom N losers

Outputs:
- ticker_stats.csv
- Console summary of top/bottom performers
"""
import os
from pathlib import Path
from typing import List, Dict, Optional, Union

import pandas as pd
from loguru import logger


class TickerAnalysis:
    """
    Analyzes trade performance by ticker.

    Attributes:
        output_dir: Directory to save CSV file
        stats: DataFrame with ticker-level statistics
    """

    CSV_FILENAME = 'ticker_stats.csv'

    def __init__(self, output_dir: Union[str, Path]):
        """
        Initialize TickerAnalysis.

        Args:
            output_dir: Directory path for CSV output
        """
        self.output_dir = str(output_dir)
        self.stats: Optional[pd.DataFrame] = None

    def analyze(self, entries: List[Dict]) -> pd.DataFrame:
        """
        Analyze trade entries and compute ticker-level statistics.

        Only EXIT entries are analyzed (they contain P&L).

        Args:
            entries: List of trade log entries

        Returns:
            DataFrame with columns: ticker, total_pnl, trade_count
        """
        if not entries:
            self.stats = pd.DataFrame(columns=['ticker', 'total_pnl', 'trade_count'])
            return self.stats

        # Convert to DataFrame
        df = pd.DataFrame(entries)

        # Filter to EXIT entries only (they have P&L)
        exit_entries = df[df['action'] == 'EXIT'].copy()

        if exit_entries.empty:
            self.stats = pd.DataFrame(columns=['ticker', 'total_pnl', 'trade_count'])
            return self.stats

        # Aggregate by ticker
        ticker_stats = exit_entries.groupby('ticker').agg(
            total_pnl=('pnl', 'sum'),
            trade_count=('pnl', 'count')
        ).reset_index()

        # Sort by P&L descending
        ticker_stats = ticker_stats.sort_values('total_pnl', ascending=False)

        self.stats = ticker_stats
        return self.stats

    def analyze_from_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Load trade log from CSV and analyze.

        Args:
            csv_path: Path to trade_log.csv

        Returns:
            DataFrame with ticker-level statistics
        """
        df = pd.read_csv(csv_path)

        # Convert to list of dicts for analyze()
        entries = df.to_dict('records')
        return self.analyze(entries)

    def get_top_winners(self, n: int = 5) -> pd.DataFrame:
        """
        Get top N winning tickers by total P&L.

        Args:
            n: Number of tickers to return

        Returns:
            DataFrame with top N winners
        """
        if self.stats is None or self.stats.empty:
            return pd.DataFrame(columns=['ticker', 'total_pnl', 'trade_count'])

        # Sort descending by P&L and take top N
        return self.stats.nlargest(min(n, len(self.stats)), 'total_pnl').reset_index(drop=True)

    def get_bottom_losers(self, n: int = 5) -> pd.DataFrame:
        """
        Get bottom N losing tickers by total P&L.

        Args:
            n: Number of tickers to return

        Returns:
            DataFrame with bottom N losers
        """
        if self.stats is None or self.stats.empty:
            return pd.DataFrame(columns=['ticker', 'total_pnl', 'trade_count'])

        # Sort ascending by P&L and take bottom N
        return self.stats.nsmallest(min(n, len(self.stats)), 'total_pnl').reset_index(drop=True)

    def save(self, filename: Optional[str] = None) -> str:
        """
        Save ticker stats to CSV file.

        Args:
            filename: Optional custom filename (default: ticker_stats.csv)

        Returns:
            Path to saved CSV file
        """
        if filename is None:
            filename = self.CSV_FILENAME

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        csv_path = os.path.join(self.output_dir, filename)

        if self.stats is not None:
            self.stats.to_csv(csv_path, index=False)
        else:
            # Empty DataFrame with headers
            pd.DataFrame(columns=['ticker', 'total_pnl', 'trade_count']).to_csv(csv_path, index=False)

        return csv_path

    def print_summary(self) -> None:
        """Print summary to console with top 5 winners and bottom 5 losers."""
        if self.stats is None or self.stats.empty:
            print("No ticker statistics available.")
            return

        print("\n" + "=" * 60)
        print("TICKER-LEVEL P&L ANALYSIS")
        print("=" * 60)

        # Top 5 Winners
        print("\nTop 5 Winners:")
        print("-" * 40)
        top_winners = self.get_top_winners(5)
        for _, row in top_winners.iterrows():
            print(f"  {row['ticker']:6s} | P&L: ${row['total_pnl']:>10,.2f} | Trades: {row['trade_count']:>3}")

        # Bottom 5 Losers
        print("\nBottom 5 Losers:")
        print("-" * 40)
        bottom_losers = self.get_bottom_losers(5)
        for _, row in bottom_losers.iterrows():
            print(f"  {row['ticker']:6s} | P&L: ${row['total_pnl']:>10,.2f} | Trades: {row['trade_count']:>3}")

        print("=" * 60)
