"""
Yahoo Finance data fetcher module using yfinance
"""
import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from loguru import logger
import time
from tenacity import retry, stop_after_attempt, wait_exponential


class YahooFinanceFetcher:
    """Yahoo Finance (yfinance) data fetcher class"""

    def __init__(self, request_delay: float = 0.5, retry_attempts: int = 3):
        """
        Initialize the fetcher.

        Args:
            request_delay: Delay between requests in seconds
            retry_attempts: Number of retry attempts on failure
        """
        self.request_delay = request_delay
        self.retry_attempts = retry_attempts

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _fetch_with_retry(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        """
        Fetch data with retry logic.

        Args:
            symbol: Ticker symbol
            period: Data period
            interval: Data interval

        Returns:
            DataFrame with OHLCV data
        """
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        return data

    def fetch_data(
        self,
        symbol: str,
        period: str = "2y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data for a single symbol.

        Args:
            symbol: Ticker symbol (e.g., "AAPL")
            period: Data period ("1y", "2y", "5y", "max")
            interval: Time interval ("1d", "1wk", "1mo")

        Returns:
            DataFrame with columns: [open, high, low, close, volume]
            Returns None on failure
        """
        try:
            data = self._fetch_with_retry(symbol, period, interval)

            if data.empty:
                logger.warning(f"{symbol}: No data available")
                return None

            # Standardize column names
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]

            # Keep only required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            available_cols = [col for col in required_cols if col in data.columns]

            if len(available_cols) < len(required_cols):
                logger.warning(f"{symbol}: Missing columns, available: {available_cols}")
                return None

            data = data[required_cols]

            # Remove rows with NaN values
            data = data.dropna()

            logger.debug(f"{symbol}: Fetched {len(data)} bars")

            # Rate limiting
            time.sleep(self.request_delay)

            return data

        except Exception as e:
            logger.error(f"{symbol}: Error fetching data - {e}")
            return None

    def fetch_multiple(
        self,
        symbols: List[str],
        period: str = "2y",
        show_progress: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols.

        Args:
            symbols: List of ticker symbols
            period: Data period
            show_progress: Show progress bar

        Returns:
            Dictionary {symbol: DataFrame}
        """
        results = {}

        if show_progress:
            from tqdm import tqdm
            symbols_iter = tqdm(symbols, desc="Fetching data")
        else:
            symbols_iter = symbols

        for symbol in symbols_iter:
            data = self.fetch_data(symbol, period=period)
            if data is not None:
                results[symbol] = data

        logger.info(f"Successfully fetched {len(results)}/{len(symbols)} symbols")
        return results

    def get_ticker_info(self, symbol: str) -> Optional[Dict]:
        """
        Get ticker information.

        Args:
            symbol: Ticker symbol

        Returns:
            Dictionary with ticker info (market cap, sector, etc.)
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'current_price': info.get('currentPrice', 0),
                'average_volume': info.get('averageVolume', 0),
            }

        except Exception as e:
            logger.error(f"{symbol}: Error fetching info - {e}")
            return None

    def filter_by_criteria(
        self,
        symbols: List[str],
        min_market_cap: float = 2_000_000_000,
        min_price: float = 5.0,
        min_volume: int = 500_000
    ) -> List[str]:
        """
        Filter symbols by market cap, price, and volume criteria.

        Args:
            symbols: List of ticker symbols
            min_market_cap: Minimum market cap
            min_price: Minimum stock price
            min_volume: Minimum average daily volume

        Returns:
            Filtered list of symbols
        """
        filtered = []

        for symbol in symbols:
            info = self.get_ticker_info(symbol)
            if info is None:
                continue

            if (info['market_cap'] >= min_market_cap and
                info['current_price'] >= min_price and
                info['average_volume'] >= min_volume):
                filtered.append(symbol)
                logger.debug(
                    f"{symbol}: Market cap ${info['market_cap']:,.0f}, "
                    f"Price ${info['current_price']:.2f}, "
                    f"Volume {info['average_volume']:,.0f}"
                )

            time.sleep(self.request_delay)

        logger.info(
            f"Filtered: {len(filtered)}/{len(symbols)} symbols meet criteria"
        )
        return filtered
