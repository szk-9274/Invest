"""
Ticker Charts Module

Generates candlestick charts with:
- SMA20 / SMA50 overlays
- ENTRY markers (up arrow)
- EXIT markers (down arrow)

Charts are generated for:
- Top 5 profitable tickers
- Bottom 5 losing tickers

Output:
- python/output/charts/{TICKER}.png
"""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple

import pandas as pd
from loguru import logger

# Try to import mplfinance, handle gracefully if not installed
try:
    import mplfinance as mpf
    MPLFINANCE_AVAILABLE = True
except ImportError:
    MPLFINANCE_AVAILABLE = False
    logger.warning("mplfinance not installed. Chart generation will be skipped.")


class TickerCharts:
    """
    Generates candlestick charts with trade markers.

    Attributes:
        output_dir: Directory to save chart images
        sma_periods: List of SMA periods for overlays
    """

    CHARTS_SUBDIR = 'charts'

    def __init__(self, output_dir: Union[str, Path]):
        """
        Initialize TickerCharts.

        Args:
            output_dir: Directory path for chart output
        """
        self.output_dir = str(output_dir)
        self.sma_periods = [20, 50]

    def create_chart(
        self,
        ticker: str,
        data: pd.DataFrame,
        trades: List[Dict],
        title: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a candlestick chart for a ticker.

        Args:
            ticker: Stock ticker symbol
            data: OHLCV DataFrame with DatetimeIndex
            trades: List of trades for this ticker (ENTRY/EXIT)
            title: Optional chart title

        Returns:
            Path to saved chart image, or None if creation failed
        """
        if not MPLFINANCE_AVAILABLE:
            logger.warning(f"Skipping chart for {ticker}: mplfinance not available")
            return None

        if data is None or data.empty:
            logger.warning(f"Skipping chart for {ticker}: no data available")
            return None

        # Ensure output directory exists
        charts_dir = os.path.join(self.output_dir, self.CHARTS_SUBDIR)
        os.makedirs(charts_dir, exist_ok=True)

        # Prepare data for mplfinance (requires DatetimeIndex and OHLCV columns)
        chart_data = data.copy()

        # Ensure column names are lowercase
        chart_data.columns = [c.lower() for c in chart_data.columns]

        # Calculate SMAs for overlay
        addplots = []
        colors = ['blue', 'orange']
        for i, period in enumerate(self.sma_periods):
            sma = chart_data['close'].rolling(window=period).mean()
            ap = mpf.make_addplot(sma, color=colors[i % len(colors)], width=1.0)
            addplots.append(ap)

        # Create entry/exit markers
        entry_dates, exit_dates = self.get_marker_dates(trades)

        # Create marker series for ENTRY (up arrows at low)
        if entry_dates:
            entry_markers = pd.Series(index=chart_data.index, dtype=float)
            for date in entry_dates:
                if date in chart_data.index:
                    entry_markers.loc[date] = chart_data.loc[date, 'low'] * 0.98
            if not entry_markers.dropna().empty:
                ap_entry = mpf.make_addplot(
                    entry_markers,
                    type='scatter',
                    markersize=100,
                    marker='^',
                    color='green'
                )
                addplots.append(ap_entry)

        # Create marker series for EXIT (down arrows at high)
        if exit_dates:
            exit_markers = pd.Series(index=chart_data.index, dtype=float)
            for date in exit_dates:
                if date in chart_data.index:
                    exit_markers.loc[date] = chart_data.loc[date, 'high'] * 1.02
            if not exit_markers.dropna().empty:
                ap_exit = mpf.make_addplot(
                    exit_markers,
                    type='scatter',
                    markersize=100,
                    marker='v',
                    color='red'
                )
                addplots.append(ap_exit)

        # Set chart title
        if title is None:
            title = f'{ticker} - Backtest Trades'

        # Save chart
        chart_path = os.path.join(charts_dir, f'{ticker}.png')

        try:
            mpf.plot(
                chart_data,
                type='candle',
                style='charles',
                title=title,
                ylabel='Price',
                volume=True,
                addplot=addplots if addplots else None,
                savefig=chart_path,
                figsize=(14, 8),
                tight_layout=True
            )
            logger.info(f"Chart saved: {chart_path}")
            return chart_path
        except Exception as e:
            logger.error(f"Failed to create chart for {ticker}: {e}")
            return None

    def create_charts_for_tickers(
        self,
        tickers: List[str],
        ticker_data: Dict[str, pd.DataFrame],
        trades_by_ticker: Dict[str, List[Dict]]
    ) -> Dict[str, str]:
        """
        Create charts for multiple tickers.

        Args:
            tickers: List of ticker symbols to chart
            ticker_data: Dict mapping ticker to OHLCV DataFrame
            trades_by_ticker: Dict mapping ticker to list of trades

        Returns:
            Dict mapping ticker to chart path (for successfully created charts)
        """
        chart_paths = {}

        for ticker in tickers:
            data = ticker_data.get(ticker)
            if data is None:
                logger.warning(f"No data available for {ticker}, skipping chart")
                continue

            trades = trades_by_ticker.get(ticker, [])
            chart_path = self.create_chart(ticker, data, trades)

            if chart_path:
                chart_paths[ticker] = chart_path

        return chart_paths

    def extract_trades_for_ticker(
        self,
        ticker: str,
        all_trades: List[Dict]
    ) -> List[Dict]:
        """
        Extract trades for a specific ticker from all trades.

        Args:
            ticker: Ticker symbol to filter
            all_trades: List of all trade entries

        Returns:
            List of trades for the specified ticker
        """
        return [t for t in all_trades if t.get('ticker') == ticker]

    def get_marker_dates(
        self,
        trades: List[Dict]
    ) -> Tuple[List[datetime], List[datetime]]:
        """
        Extract entry and exit dates from trades.

        Args:
            trades: List of trade entries for a ticker

        Returns:
            Tuple of (entry_dates, exit_dates)
        """
        entry_dates = []
        exit_dates = []

        for trade in trades:
            date = trade.get('date')
            action = trade.get('action')

            if date and action == 'ENTRY':
                entry_dates.append(date)
            elif date and action == 'EXIT':
                exit_dates.append(date)

        return entry_dates, exit_dates

    def generate_top_bottom_charts(
        self,
        ticker_data: Dict[str, pd.DataFrame],
        trades: List[Dict],
        top_tickers: List[str],
        bottom_tickers: List[str]
    ) -> Dict[str, str]:
        """
        Generate charts for top winners and bottom losers.

        Args:
            ticker_data: Dict mapping ticker to OHLCV DataFrame
            trades: All trade entries
            top_tickers: List of top performing ticker symbols
            bottom_tickers: List of bottom performing ticker symbols

        Returns:
            Dict mapping ticker to chart path
        """
        # Combine top and bottom tickers
        all_tickers = list(set(top_tickers + bottom_tickers))

        # Build trades by ticker
        trades_by_ticker = {}
        for ticker in all_tickers:
            trades_by_ticker[ticker] = self.extract_trades_for_ticker(ticker, trades)

        return self.create_charts_for_tickers(all_tickers, ticker_data, trades_by_ticker)
