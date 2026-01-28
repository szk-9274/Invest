"""
Yahoo Finance data fetcher module using yfinance
with local cache support and rate-limit handling
"""
import yfinance as yf
import pandas as pd
import pickle
from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger
import time
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# Default cache directory
DEFAULT_CACHE_DIR = Path(__file__).parent.parent / "cache"


class YahooFinanceFetcher:
    """Yahoo Finance (yfinance) data fetcher class with caching"""

    def __init__(
        self,
        request_delay: float = 0.5,
        retry_attempts: int = 3,
        cache_dir: Optional[str] = None,
        cache_enabled: bool = True,
        cache_max_age_hours: int = 12,
    ):
        """
        Initialize the fetcher.

        Args:
            request_delay: Delay between requests in seconds
            retry_attempts: Number of retry attempts on failure
            cache_dir: Directory for local cache files
            cache_enabled: Enable/disable caching
            cache_max_age_hours: Maximum age of cache files in hours
        """
        self.request_delay = request_delay
        self.retry_attempts = retry_attempts
        self.cache_enabled = cache_enabled
        self.cache_max_age_hours = cache_max_age_hours

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = DEFAULT_CACHE_DIR

        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, symbol: str, period: str, interval: str) -> str:
        """Generate a cache key for the given parameters."""
        raw = f"{symbol}_{period}_{interval}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _cache_path(self, symbol: str, period: str, interval: str) -> Path:
        """Get the cache file path."""
        key = self._cache_key(symbol, period, interval)
        return self.cache_dir / f"{symbol}_{key}.pkl"

    def _load_from_cache(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """Load data from local cache if valid."""
        if not self.cache_enabled:
            return None

        cache_file = self._cache_path(symbol, period, interval)
        if not cache_file.exists():
            return None

        # Check age
        import os
        age_seconds = time.time() - os.path.getmtime(str(cache_file))
        age_hours = age_seconds / 3600

        if age_hours > self.cache_max_age_hours:
            logger.debug(f"{symbol}: Cache expired ({age_hours:.1f}h > {self.cache_max_age_hours}h)")
            return None

        try:
            with open(cache_file, "rb") as f:
                data = pickle.load(f)
            logger.debug(f"{symbol}: Loaded from cache ({len(data)} bars, {age_hours:.1f}h old)")
            return data
        except Exception as e:
            logger.warning(f"{symbol}: Cache read error - {e}")
            return None

    def _save_to_cache(self, symbol: str, period: str, interval: str, data: pd.DataFrame) -> None:
        """Save data to local cache."""
        if not self.cache_enabled:
            return

        cache_file = self._cache_path(symbol, period, interval)
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
            logger.debug(f"{symbol}: Saved to cache")
        except Exception as e:
            logger.warning(f"{symbol}: Cache write error - {e}")

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=3, max=60),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True,
    )
    def _fetch_with_retry(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        """
        Fetch data with retry logic (exponential backoff).

        Args:
            symbol: Ticker symbol
            period: Data period
            interval: Data interval

        Returns:
            DataFrame with OHLCV data
        """
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        if data.empty:
            raise ValueError(f"{symbol}: No data returned from yfinance")
        return data

    def fetch_data(
        self,
        symbol: str,
        period: str = "2y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data for a single symbol (with cache).

        Args:
            symbol: Ticker symbol (e.g., "AAPL")
            period: Data period ("1y", "2y", "5y", "max")
            interval: Time interval ("1d", "1wk", "1mo")

        Returns:
            DataFrame with columns: [open, high, low, close, volume]
            Returns None on failure
        """
        # Try cache first
        cached = self._load_from_cache(symbol, period, interval)
        if cached is not None:
            return cached

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

            # Save to cache
            self._save_to_cache(symbol, period, interval, data)

            # Rate limiting
            time.sleep(self.request_delay)

            return data

        except Exception as e:
            logger.error(f"{symbol}: Error fetching data - {e}")
            return None

    def fetch_benchmark(
        self,
        symbol: str = "SPY",
        period: str = "2y",
    ) -> Optional[pd.DataFrame]:
        """
        Fetch benchmark data with more aggressive retry and longer cache.

        SPY fetch is allowed to take longer; uses extended retry and
        a dedicated cache with a longer TTL.

        Args:
            symbol: Benchmark symbol (default "SPY")
            period: Data period

        Returns:
            DataFrame or None
        """
        # Use a longer cache TTL for benchmark
        cache_file = self.cache_dir / f"benchmark_{symbol}_{period}.pkl"

        if self.cache_enabled and cache_file.exists():
            import os
            age_hours = (time.time() - os.path.getmtime(str(cache_file))) / 3600
            # Benchmark cache valid for 24 hours
            if age_hours < 24:
                try:
                    with open(cache_file, "rb") as f:
                        data = pickle.load(f)
                    logger.info(f"Benchmark {symbol}: Loaded from cache ({len(data)} bars, {age_hours:.1f}h old)")
                    return data
                except Exception:
                    pass

        logger.info(f"Fetching benchmark data ({symbol})...")

        # Try with more retries and longer backoff for benchmark
        max_attempts = 7
        for attempt in range(1, max_attempts + 1):
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, interval="1d")

                if data.empty:
                    logger.warning(f"Benchmark {symbol}: Attempt {attempt} - empty response")
                    wait_time = min(2 ** attempt, 120)
                    time.sleep(wait_time)
                    continue

                # Standardize
                data.columns = [col.lower().replace(' ', '_') for col in data.columns]
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                available_cols = [col for col in required_cols if col in data.columns]
                if len(available_cols) < len(required_cols):
                    logger.warning(f"Benchmark {symbol}: Missing columns")
                    continue

                data = data[required_cols].dropna()

                # Save to dedicated benchmark cache
                if self.cache_enabled:
                    try:
                        self.cache_dir.mkdir(parents=True, exist_ok=True)
                        with open(cache_file, "wb") as f:
                            pickle.dump(data, f)
                    except Exception as e:
                        logger.warning(f"Benchmark cache write error: {e}")

                logger.info(f"Benchmark {symbol}: Fetched {len(data)} bars")
                time.sleep(self.request_delay)
                return data

            except Exception as e:
                logger.warning(f"Benchmark {symbol}: Attempt {attempt}/{max_attempts} failed - {e}")
                wait_time = min(2 ** attempt, 120)
                time.sleep(wait_time)

        logger.error(f"Benchmark {symbol}: All {max_attempts} attempts failed")
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
