"""
Ticker Charts Module

Phase 1: TradingView-like Price Chart Generator
Generates candlestick charts with:
- Dark background (TradingView-like)
- SMA 20, 50, 200 overlays
- Bollinger Bands (20, 2)
- Volume panel below price
- Clean layout with monthly date ticks

Phase 2: Trade Markers and Auto-Generation
- ENTRY markers (up arrow, green)
- EXIT markers (down arrow, red)
- Auto-generate top/bottom P&L charts after backtest

Output:
- output/charts/{TICKER}_price_chart.png
- output/charts/top_01_{TICKER}.png
- output/charts/bottom_01_{TICKER}.png
"""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple

import pandas as pd
import numpy as np
from loguru import logger

# Try to import mplfinance, handle gracefully if not installed
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for headless operation
    import mplfinance as mpf
    import matplotlib.pyplot as plt
    MPLFINANCE_AVAILABLE = True
except ImportError:
    MPLFINANCE_AVAILABLE = False
    mpf = None
    plt = None
    matplotlib = None
    logger.warning("mplfinance not installed. Chart generation will be skipped.")

# Try to import yfinance for data fetching
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None
    logger.warning("yfinance not installed. Data fetching will not be available.")


# Minimum data points required for SMA200
MIN_DATA_POINTS = 50

# Default timezone for financial data (US markets)
DEFAULT_TIMEZONE = 'America/New_York'


def normalize_timestamp(
    ts: Union[str, datetime, pd.Timestamp],
    target_tz: str = DEFAULT_TIMEZONE
) -> pd.Timestamp:
    """
    Normalize a timestamp to the target timezone (default: America/New_York).

    This function ensures consistent timezone handling across the codebase:
    - If tz-naive: localize to target timezone
    - If tz-aware: convert to target timezone
    - Accepts strings, datetime objects, and pd.Timestamp

    Args:
        ts: Input timestamp (string, datetime, or pd.Timestamp)
        target_tz: Target timezone (default: America/New_York)

    Returns:
        pd.Timestamp with target timezone

    Example:
        >>> normalize_timestamp('2024-03-15')
        Timestamp('2024-03-15 00:00:00-0400', tz='America/New_York')
        >>> normalize_timestamp(pd.Timestamp('2024-03-15 14:30:00', tz='UTC'))
        Timestamp('2024-03-15 10:30:00-0400', tz='America/New_York')
    """
    # Convert to pd.Timestamp if needed
    if isinstance(ts, str):
        ts = pd.Timestamp(ts)
    elif isinstance(ts, datetime) and not isinstance(ts, pd.Timestamp):
        ts = pd.Timestamp(ts)

    # Handle timezone
    if ts.tzinfo is None:
        # Timezone-naive: localize to target timezone
        return ts.tz_localize(target_tz)
    else:
        # Timezone-aware: convert to target timezone
        return ts.tz_convert(target_tz)


def _create_tradingview_style() -> dict:
    """
    Create a TradingView-like dark style for mplfinance.

    Returns:
        Style dictionary for mplfinance
    """
    if not MPLFINANCE_AVAILABLE:
        return {}

    # TradingView dark mode colors
    tradingview_style = mpf.make_mpf_style(
        base_mpf_style='nightclouds',
        marketcolors=mpf.make_marketcolors(
            up='#26a69a',       # Green for up candles
            down='#ef5350',     # Red for down candles
            edge='inherit',
            wick='inherit',
            volume={'up': '#26a69a', 'down': '#ef5350'},
        ),
        facecolor='#131722',    # Dark background
        edgecolor='#2a2e39',
        figcolor='#131722',
        gridcolor='#2a2e39',
        gridstyle='-',
        gridaxis='both',
        y_on_right=True,
        rc={
            'axes.labelcolor': '#787b86',
            'axes.titlecolor': '#d1d4dc',
            'xtick.color': '#787b86',
            'ytick.color': '#787b86',
            'text.color': '#d1d4dc',
            'figure.facecolor': '#131722',
            'axes.facecolor': '#131722',
        }
    )
    return tradingview_style


def _normalize_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DataFrame column names to match mplfinance requirements.

    Args:
        data: OHLCV DataFrame

    Returns:
        Normalized DataFrame with proper column names

    Raises:
        ValueError: If required columns are missing
    """
    if data is None:
        raise ValueError("Data cannot be None")

    if data.empty:
        raise ValueError("No data available for chart generation")

    df = data.copy()

    # Normalize column names to title case (mplfinance expects Open, High, Low, Close, Volume)
    column_mapping = {}
    required_cols = {'open', 'high', 'low', 'close', 'volume'}
    found_cols = set()

    for col in df.columns:
        col_lower = col.lower()
        if col_lower in required_cols:
            column_mapping[col] = col_lower.title()
            found_cols.add(col_lower)

    # Check for missing columns
    missing_cols = required_cols - found_cols
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df = df.rename(columns=column_mapping)

    # Ensure DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception as e:
            raise ValueError(f"Cannot convert index to DatetimeIndex: {e}")

    return df


def _parse_trade_log(
    trade_log_path: Optional[str],
    ticker: str
) -> Tuple[List, List]:
    """
    Parse trade_log.csv and extract ENTRY/EXIT dates for a specific ticker.

    Args:
        trade_log_path: Path to trade_log.csv file (can be None)
        ticker: Ticker symbol to filter trades for

    Returns:
        Tuple of (entry_dates, exit_dates) as lists of Timestamps
    """
    entry_dates = []
    exit_dates = []

    if trade_log_path is None:
        return entry_dates, exit_dates

    # Log the resolved path for debugging
    abs_path = os.path.abspath(trade_log_path)
    logger.debug(f"Looking for trade_log at: {abs_path}")

    # Check if file exists
    if not os.path.exists(trade_log_path):
        logger.debug(f"Trade log not found: {abs_path} (cwd: {os.getcwd()})")
        return entry_dates, exit_dates

    try:
        df = pd.read_csv(trade_log_path)

        if df.empty:
            return entry_dates, exit_dates

        # Filter by ticker
        ticker_trades = df[df['ticker'] == ticker]

        if ticker_trades.empty:
            return entry_dates, exit_dates

        # Convert date column to datetime and normalize to America/New_York timezone
        # CRITICAL: trade_log.csv dates are stored as tz-naive strings (YYYY-MM-DD)
        # but OHLCV data from yfinance is tz-aware (America/New_York).
        # We must normalize to avoid "Invalid comparison between tz-aware and tz-naive" errors.
        ticker_trades = ticker_trades.copy()
        ticker_trades['date'] = pd.to_datetime(ticker_trades['date']).apply(normalize_timestamp)

        # Extract ENTRY dates (now timezone-aware)
        entries = ticker_trades[ticker_trades['action'] == 'ENTRY']
        entry_dates = entries['date'].tolist()

        # Extract EXIT dates (now timezone-aware)
        exits = ticker_trades[ticker_trades['action'] == 'EXIT']
        exit_dates = exits['date'].tolist()

    except Exception as e:
        logger.warning(f"Failed to parse trade log: {e}")

    return entry_dates, exit_dates


def _create_trade_markers(
    data: pd.DataFrame,
    entry_dates: List,
    exit_dates: List
) -> List:
    """
    Create mplfinance addplot objects for trade markers.

    CRITICAL: Both data.index and entry_dates/exit_dates must have matching timezone
    awareness. This function expects timezone-aware timestamps (America/New_York).

    Args:
        data: Normalized OHLCV DataFrame (must have DatetimeIndex, timezone-aware preferred)
        entry_dates: List of ENTRY dates (should be timezone-aware)
        exit_dates: List of EXIT dates (should be timezone-aware)

    Returns:
        List of mplfinance addplot objects for markers
    """
    if not MPLFINANCE_AVAILABLE:
        return []

    addplots = []

    # Determine if data index is timezone-aware
    data_tz = data.index.tz

    def _normalize_date_for_comparison(date):
        """Normalize date to match data index timezone."""
        if data_tz is not None:
            # Data is tz-aware, normalize date to same timezone
            return normalize_timestamp(date, str(data_tz))
        else:
            # Data is tz-naive, strip timezone from date if present
            if hasattr(date, 'tzinfo') and date.tzinfo is not None:
                return date.tz_localize(None)
            return pd.Timestamp(date)

    def _find_date_in_index(date, data_index):
        """
        Find a date in the data index, handling timezone-aware comparisons.

        Returns: (found_date, price_column_value) or (None, None)
        """
        normalized_date = _normalize_date_for_comparison(date)

        # Direct lookup first
        if normalized_date in data_index:
            return normalized_date, True

        # Try to find closest date >= target
        try:
            mask = data_index >= normalized_date
            if mask.any():
                closest = data_index[mask][0]
                return closest, True
        except TypeError:
            # Timezone mismatch - log warning and skip
            logger.warning(f"Timezone mismatch when finding date {date} in index")
            return None, False

        return None, False

    # Create marker series for ENTRY (up arrows at low)
    if entry_dates:
        entry_markers = pd.Series(index=data.index, dtype=float)
        for date in entry_dates:
            found_date, success = _find_date_in_index(date, data.index)
            if success and found_date is not None:
                entry_markers.loc[found_date] = data.loc[found_date, 'Low'] * 0.98

        if not entry_markers.dropna().empty:
            ap_entry = mpf.make_addplot(
                entry_markers,
                type='scatter',
                markersize=120,
                marker='^',
                color='#26a69a'  # Green (TradingView style)
            )
            addplots.append(ap_entry)

    # Create marker series for EXIT (down arrows at high)
    if exit_dates:
        exit_markers = pd.Series(index=data.index, dtype=float)
        for date in exit_dates:
            found_date, success = _find_date_in_index(date, data.index)
            if success and found_date is not None:
                exit_markers.loc[found_date] = data.loc[found_date, 'High'] * 1.02

        if not exit_markers.dropna().empty:
            ap_exit = mpf.make_addplot(
                exit_markers,
                type='scatter',
                markersize=120,
                marker='v',
                color='#ef5350'  # Red (TradingView style)
            )
            addplots.append(ap_exit)

    return addplots


def _calculate_indicators(data: pd.DataFrame) -> List:
    """
    Calculate technical indicators for the chart.

    Args:
        data: Normalized OHLCV DataFrame

    Returns:
        List of mplfinance addplot objects
    """
    if not MPLFINANCE_AVAILABLE:
        return []

    addplots = []

    close = data['Close']

    # SMA 20 (cyan/turquoise)
    sma20 = close.rolling(window=20).mean()
    addplots.append(mpf.make_addplot(
        sma20,
        color='#00bcd4',
        width=1.0,
        label='SMA20'
    ))

    # SMA 50 (yellow/gold)
    sma50 = close.rolling(window=50).mean()
    addplots.append(mpf.make_addplot(
        sma50,
        color='#ffeb3b',
        width=1.0,
        label='SMA50'
    ))

    # SMA 200 (magenta/pink)
    sma200 = close.rolling(window=200).mean()
    addplots.append(mpf.make_addplot(
        sma200,
        color='#e91e63',
        width=1.0,
        label='SMA200'
    ))

    # Bollinger Bands (20, 2)
    bb_middle = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    bb_upper = bb_middle + (bb_std * 2)
    bb_lower = bb_middle - (bb_std * 2)

    # Upper band (gray, dashed effect via alpha)
    addplots.append(mpf.make_addplot(
        bb_upper,
        color='#9e9e9e',
        width=0.8,
        linestyle='--',
        alpha=0.7
    ))

    # Lower band (gray, dashed effect via alpha)
    addplots.append(mpf.make_addplot(
        bb_lower,
        color='#9e9e9e',
        width=0.8,
        linestyle='--',
        alpha=0.7
    ))

    return addplots


def generate_price_chart_from_dataframe(
    ticker: str,
    data: pd.DataFrame,
    output_dir: str,
    style: str = "tradingview",
    trade_log_path: Optional[str] = None,
    output_filename: Optional[str] = None
) -> Path:
    """
    Generate a TradingView-like price chart from a DataFrame.

    This is the core chart generation function that accepts data directly.
    Use generate_price_chart() if you want to fetch data automatically.

    Args:
        ticker: Stock ticker symbol
        data: OHLCV DataFrame with DatetimeIndex
        output_dir: Directory path for chart output
        style: Chart style ("tradingview" for dark mode)
        trade_log_path: Optional path to trade_log.csv for IN/OUT markers (Phase 2)
        output_filename: Optional custom filename for the chart

    Returns:
        Path to saved chart image

    Raises:
        ValueError: If data is missing, empty, or has insufficient rows
        RuntimeError: If chart generation fails
    """
    if not MPLFINANCE_AVAILABLE:
        raise RuntimeError("mplfinance not installed. Cannot generate charts.")

    # Normalize data
    chart_data = _normalize_dataframe(data)

    # Check minimum data points
    if len(chart_data) < MIN_DATA_POINTS:
        raise ValueError(
            f"Insufficient data for chart generation. "
            f"Minimum {MIN_DATA_POINTS} data points required, got {len(chart_data)}."
        )

    # Create output directory
    charts_dir = Path(output_dir) / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    # Determine filename
    if output_filename:
        chart_path = charts_dir / output_filename
    else:
        # Sanitize ticker for filename (replace dots with dashes)
        safe_ticker = ticker.replace('.', '-')
        chart_path = charts_dir / f"{safe_ticker}_price_chart.png"

    # Get style
    chart_style = _create_tradingview_style() if style == "tradingview" else 'charles'

    # Calculate indicators
    addplots = _calculate_indicators(chart_data)

    # Parse trade log and add markers (Phase 2)
    if trade_log_path:
        entry_dates, exit_dates = _parse_trade_log(trade_log_path, ticker)
        marker_plots = _create_trade_markers(chart_data, entry_dates, exit_dates)
        addplots.extend(marker_plots)

    # Generate chart
    try:
        fig, axes = mpf.plot(
            chart_data,
            type='candle',
            style=chart_style,
            title=f'{ticker} - Price Chart',
            ylabel='Price',
            ylabel_lower='Volume',
            volume=True,
            addplot=addplots if addplots else None,
            figsize=(16, 10),
            tight_layout=True,
            returnfig=True,
            panel_ratios=(3, 1),  # Price panel 3x larger than volume
            xrotation=0,
            datetime_format='%b %Y',  # Monthly date format
        )

        # Save figure
        fig.savefig(
            chart_path,
            dpi=100,
            bbox_inches='tight',
            facecolor='#131722' if style == "tradingview" else 'white',
            edgecolor='none'
        )
        plt.close(fig)

        logger.info(f"Chart generated: {chart_path}")
        return chart_path

    except Exception as e:
        logger.error(f"Failed to generate chart for {ticker}: {e}")
        raise RuntimeError(f"Chart generation failed for {ticker}: {e}")


def generate_price_chart(
    ticker: str,
    start_date: str,
    end_date: str,
    output_dir: str,
    style: str = "tradingview",
    trade_log_path: Optional[str] = None
) -> Path:
    """
    Generate a TradingView-like price chart by fetching data from yfinance.

    This function fetches ~1 year of data and generates a candlestick chart
    with SMA 20/50/200, Bollinger Bands, and volume panel.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        output_dir: Directory path for chart output
        style: Chart style ("tradingview" for dark mode, default)
        trade_log_path: Optional path to trade_log.csv for IN/OUT markers (Phase 2)

    Returns:
        Path to saved chart image

    Raises:
        ValueError: If data is missing or has insufficient rows
        RuntimeError: If chart generation fails
    """
    if not YFINANCE_AVAILABLE:
        raise RuntimeError("yfinance not installed. Cannot fetch data.")

    # Fetch data from yfinance
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)

    if data is None or data.empty:
        raise ValueError(f"No data available for ticker {ticker} from {start_date} to {end_date}")

    return generate_price_chart_from_dataframe(
        ticker=ticker,
        data=data,
        output_dir=output_dir,
        style=style,
        trade_log_path=trade_log_path
    )


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


def generate_top_bottom_charts(
    ticker_stats_path: str,
    trade_log_path: str,
    output_dir: str,
    top_n: int = 5,
    bottom_n: int = 5,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Path]:
    """
    Generate charts for top N winners and bottom N losers based on P&L.

    This function reads ticker_stats.csv to identify top/bottom performers,
    then generates TradingView-style charts with IN/OUT markers for each.

    Args:
        ticker_stats_path: Path to ticker_stats.csv
        trade_log_path: Path to trade_log.csv
        output_dir: Directory path for chart output
        top_n: Number of top performing tickers to chart (default 5)
        bottom_n: Number of bottom performing tickers to chart (default 5)
        start_date: Optional start date for data fetch (YYYY-MM-DD)
        end_date: Optional end date for data fetch (YYYY-MM-DD)

    Returns:
        List of Path objects to generated charts

    Raises:
        RuntimeError: If required dependencies are not available
    """
    if not YFINANCE_AVAILABLE:
        raise RuntimeError("yfinance not installed. Cannot fetch data.")

    if not MPLFINANCE_AVAILABLE:
        raise RuntimeError("mplfinance not installed. Cannot generate charts.")

    # Load ticker stats
    if not os.path.exists(ticker_stats_path):
        logger.warning(f"Ticker stats not found: {ticker_stats_path}")
        return []

    try:
        stats_df = pd.read_csv(ticker_stats_path)
    except Exception as e:
        logger.error(f"Failed to read ticker stats: {e}")
        return []

    if stats_df.empty:
        logger.warning("Ticker stats is empty")
        return []

    # Ensure sorted by P&L descending
    stats_df = stats_df.sort_values('total_pnl', ascending=False)

    # Get top N tickers
    top_tickers = stats_df.head(min(top_n, len(stats_df)))['ticker'].tolist() if top_n > 0 else []

    # Get bottom N tickers
    bottom_tickers = stats_df.tail(min(bottom_n, len(stats_df)))['ticker'].tolist() if bottom_n > 0 else []

    # Calculate default date range (1 year)
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        start_dt = datetime.now() - pd.DateOffset(years=1)
        start_date = start_dt.strftime('%Y-%m-%d')

    # Generate charts
    chart_paths = []
    charts_dir = Path(output_dir) / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    # Generate top ticker charts
    for idx, ticker in enumerate(top_tickers, start=1):
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)

            if data is None or data.empty or len(data) < MIN_DATA_POINTS:
                logger.warning(f"Insufficient data for {ticker}, skipping")
                continue

            filename = f"top_{idx:02d}_{ticker}.png"
            chart_path = generate_price_chart_from_dataframe(
                ticker=ticker,
                data=data,
                output_dir=output_dir,
                style="tradingview",
                trade_log_path=trade_log_path,
                output_filename=filename
            )
            chart_paths.append(chart_path)
            logger.info(f"Generated top chart: {filename}")

        except Exception as e:
            logger.error(f"Failed to generate chart for {ticker}: {e}")

    # Generate bottom ticker charts
    for idx, ticker in enumerate(bottom_tickers, start=1):
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)

            if data is None or data.empty or len(data) < MIN_DATA_POINTS:
                logger.warning(f"Insufficient data for {ticker}, skipping")
                continue

            filename = f"bottom_{idx:02d}_{ticker}.png"
            chart_path = generate_price_chart_from_dataframe(
                ticker=ticker,
                data=data,
                output_dir=output_dir,
                style="tradingview",
                trade_log_path=trade_log_path,
                output_filename=filename
            )
            chart_paths.append(chart_path)
            logger.info(f"Generated bottom chart: {filename}")

        except Exception as e:
            logger.error(f"Failed to generate chart for {ticker}: {e}")

    return chart_paths
