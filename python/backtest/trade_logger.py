"""
Trade Logger Module

Provides persistent logging of trade actions (ENTRY/EXIT) to CSV format.
Designed for post-backtest analysis and verification.

CSV Format:
    date,ticker,action,price,shares,reason,pnl,capital_after

Actions:
    ENTRY - Opening a new position
    EXIT  - Closing an existing position

Exit Reasons:
    stop_loss       - Price hit stop loss level
    ma50_break      - Price broke below 50-day MA
    target_reached  - Price reached target price
    end_of_backtest - Position closed at backtest end
"""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union

import pandas as pd


class TradeLogger:
    """
    Logs trade actions to CSV for post-backtest analysis.

    Attributes:
        output_dir: Directory to save CSV file
        entries: List of trade log entries
    """

    CSV_COLUMNS = ['date', 'ticker', 'action', 'price', 'shares', 'reason', 'pnl', 'capital_after']
    CSV_FILENAME = 'trade_log.csv'

    def __init__(self, output_dir: Union[str, Path]):
        """
        Initialize TradeLogger.

        Args:
            output_dir: Directory path for CSV output
        """
        self.output_dir = str(output_dir)
        self.entries: List[Dict] = []

    def log_entry(
        self,
        date: datetime,
        ticker: str,
        price: float,
        shares: int,
        reason: str,
        capital_after: float
    ) -> None:
        """
        Log an ENTRY action (position opened).

        Args:
            date: Date of entry
            ticker: Stock ticker symbol
            price: Entry price
            shares: Number of shares
            reason: Reason for entry
            capital_after: Capital remaining after entry
        """
        entry = {
            'date': date,
            'ticker': ticker,
            'action': 'ENTRY',
            'price': price,
            'shares': shares,
            'reason': reason,
            'pnl': None,  # ENTRY has no P&L
            'capital_after': capital_after
        }
        self.entries.append(entry)

    def log_exit(
        self,
        date: datetime,
        ticker: str,
        price: float,
        shares: int,
        reason: str,
        pnl: float,
        capital_after: float
    ) -> None:
        """
        Log an EXIT action (position closed).

        Args:
            date: Date of exit
            ticker: Stock ticker symbol
            price: Exit price
            shares: Number of shares
            reason: Exit reason (stop_loss, ma50_break, target_reached, end_of_backtest)
            pnl: Profit/loss from the trade
            capital_after: Capital after exit
        """
        entry = {
            'date': date,
            'ticker': ticker,
            'action': 'EXIT',
            'price': price,
            'shares': shares,
            'reason': reason,
            'pnl': pnl,
            'capital_after': capital_after
        }
        self.entries.append(entry)

    def save(self, filename: Optional[str] = None) -> str:
        """
        Save trade log to CSV file.

        Args:
            filename: Optional custom filename (default: trade_log.csv)

        Returns:
            Path to saved CSV file
        """
        if filename is None:
            filename = self.CSV_FILENAME

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        csv_path = os.path.join(self.output_dir, filename)

        # Convert entries to DataFrame
        if self.entries:
            df = pd.DataFrame(self.entries, columns=self.CSV_COLUMNS)
            # Format dates as YYYY-MM-DD
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        else:
            # Empty DataFrame with headers
            df = pd.DataFrame(columns=self.CSV_COLUMNS)

        df.to_csv(csv_path, index=False)
        return csv_path

    def get_entries_df(self) -> pd.DataFrame:
        """
        Get all entries as a DataFrame.

        Returns:
            DataFrame with all logged entries
        """
        if self.entries:
            df = pd.DataFrame(self.entries, columns=self.CSV_COLUMNS)
            return df
        return pd.DataFrame(columns=self.CSV_COLUMNS)

    def get_exit_entries(self) -> List[Dict]:
        """
        Get only EXIT entries.

        Returns:
            List of EXIT action entries
        """
        return [e for e in self.entries if e['action'] == 'EXIT']

    def clear(self) -> None:
        """Clear all logged entries."""
        self.entries = []
