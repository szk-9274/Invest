"""
Extended Ticker List Update Script
Fetches approximately 3,500 tickers from S&P 500, NASDAQ, and Russell 3000
"""
import pandas as pd
import warnings
from io import StringIO

# Suppress yfinance DeprecationWarning before import
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*Ticker.earnings.*")

import yfinance as yf
import requests
from typing import List, Set, Dict, Optional
from pathlib import Path
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.ticker_normalizer import normalize_tickers


class TickerFetcher:
    """Fetches and filters ticker symbols from multiple sources"""

    def __init__(
        self,
        min_market_cap: float = 2_000_000_000,
        min_price: float = 5.0,
        min_volume: int = 500_000,
        max_tickers: int = 3500,
        request_delay: float = 0.3
    ):
        """
        Initialize the ticker fetcher.

        Args:
            min_market_cap: Minimum market cap in USD (default: 2B)
            min_price: Minimum stock price (default: $5)
            min_volume: Minimum average daily volume (default: 500K)
            max_tickers: Maximum number of tickers to return (default: 3500)
            request_delay: Delay between API requests in seconds
        """
        self.min_market_cap = min_market_cap
        self.min_price = min_price
        self.min_volume = min_volume
        self.max_tickers = max_tickers
        self.request_delay = request_delay
        self.exclude_types = ['ETF', 'REIT', 'ADR', 'CEF']

    def fetch_sp500(self) -> List[str]:
        """
        Fetch S&P 500 tickers from Wikipedia.

        Returns:
            List of S&P 500 ticker symbols
        """
        logger.info("Fetching S&P 500 tickers from Wikipedia...")
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            # Use requests with User-Agent header to avoid 403 Forbidden
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            # Parse HTML response with pandas (use StringIO to avoid FutureWarning)
            tables = pd.read_html(StringIO(response.text), flavor='lxml')
            df = tables[0]
            tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
            logger.info(f"[OK] S&P 500: Fetched {len(tickers)} tickers")
            return tickers
        except Exception as e:
            logger.error(f"[FAIL] S&P 500 fetch failed: {type(e).__name__}: {e}")
            logger.warning("Attempting fallback sources for S&P 500...")
            # Fallback: Try alternative sources or use empty list
            return []

    def fetch_nasdaq_composite(self) -> List[str]:
        """
        Fetch NASDAQ listed tickers via ftp.nasdaqtrader.com.

        Returns:
            List of NASDAQ ticker symbols
        """
        logger.info("Fetching NASDAQ tickers...")
        try:
            # NASDAQ Trader FTP provides comprehensive lists
            url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
            df = pd.read_csv(url, sep='|')
            # Filter out test issues and non-stock entries
            df = df[df['Test Issue'] == 'N']
            tickers = df['Symbol'].dropna().tolist()
            # Remove last row which is usually a file creation timestamp
            if tickers and 'File Creation Time' in str(tickers[-1]):
                tickers = tickers[:-1]
            logger.info(f"[OK] NASDAQ: Fetched {len(tickers)} tickers")
            return tickers
        except Exception as e:
            logger.error(f"[FAIL] NASDAQ fetch failed: {type(e).__name__}: {e}")
            return []

    def fetch_nyse_listed(self) -> List[str]:
        """
        Fetch NYSE listed tickers.

        Returns:
            List of NYSE ticker symbols
        """
        logger.info("Fetching NYSE tickers...")
        try:
            url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
            df = pd.read_csv(url, sep='|')
            # Filter for NYSE
            df = df[df['Exchange'] == 'N']
            df = df[df['Test Issue'] == 'N']
            tickers = df['ACT Symbol'].dropna().tolist()
            if tickers and 'File Creation Time' in str(tickers[-1]):
                tickers = tickers[:-1]
            logger.info(f"[OK] NYSE: Fetched {len(tickers)} tickers")
            return tickers
        except Exception as e:
            logger.error(f"[FAIL] NYSE fetch failed: {type(e).__name__}: {e}")
            return []

    def fetch_russell3000_proxy(self) -> List[str]:
        """
        Fetch Russell 3000 proxy via iShares ETF holdings.
        Uses IWV (iShares Russell 3000 ETF) holdings.

        Returns:
            List of Russell 3000 ticker symbols
        """
        logger.info("Fetching Russell 3000 proxy (IWV holdings)...")
        try:
            # Try to get IWV holdings from iShares
            url = "https://www.ishares.com/us/products/239714/ishares-russell-3000-etf/1467271812596.ajax?fileType=csv&fileName=IWV_holdings&dataType=fund"
            df = pd.read_csv(url, skiprows=9)
            if 'Ticker' in df.columns:
                tickers = df['Ticker'].dropna().tolist()
                # Clean up tickers
                tickers = [t.strip() for t in tickers if isinstance(t, str) and t.strip()]
                logger.info(f"[OK] Russell 3000 (IWV): Fetched {len(tickers)} tickers")
                return tickers
        except Exception as e:
            logger.warning(f"[WARN] Russell 3000 (IWV) fetch failed: {type(e).__name__}: {e}")

        # Fallback: return empty list, will rely on other sources
        logger.warning("Using NASDAQ + NYSE as Russell 3000 proxy")
        return []

    def get_ticker_info_batch(
        self,
        tickers: List[str],
        max_workers: int = 4
    ) -> dict:
        """
        Get ticker info for multiple symbols in parallel.

        Args:
            tickers: List of ticker symbols
            max_workers: Number of parallel workers

        Returns:
            Dictionary with 'info' (dict) and 'stats' (dict)
        """
        results = {}
        stats = {
            'success': 0,
            'failed': 0,
            'total': len(tickers)
        }

        def fetch_single(ticker: str) -> tuple:
            try:
                time.sleep(self.request_delay)
                stock = yf.Ticker(ticker)
                info = stock.info
                return ticker, {
                    'market_cap': info.get('marketCap', 0),
                    'current_price': info.get('currentPrice', 0) or info.get('regularMarketPrice', 0),
                    'average_volume': info.get('averageVolume', 0),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown'),
                    'quote_type': info.get('quoteType', 'Unknown'),
                    'exchange': info.get('exchange', 'Unknown'),
                    'long_name': info.get('longName', ticker)
                }
            except Exception as e:
                logger.debug(f"{ticker}: Error fetching info - {type(e).__name__}: {e}")
                return ticker, None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_single, t): t for t in tickers}

            for future in tqdm(as_completed(futures), total=len(tickers), desc="Fetching ticker info"):
                ticker, info = future.result()
                if info is not None:
                    results[ticker] = info
                    stats['success'] += 1
                else:
                    stats['failed'] += 1

        logger.info(f"Info fetch: {stats['success']:,} succeeded, {stats['failed']:,} failed (total: {stats['total']:,})")

        return {
            'info': results,
            'stats': stats
        }

    def filter_tickers(self, ticker_info: Dict[str, Dict]) -> dict:
        """
        Filter tickers based on criteria.

        Args:
            ticker_info: Dictionary of ticker info

        Returns:
            Dictionary with 'tickers' (list) and 'filter_stats' (dict)
        """
        filtered = []
        filter_stats = {
            'total_checked': len(ticker_info),
            'excluded_market_cap': 0,
            'excluded_price': 0,
            'excluded_volume': 0,
            'excluded_type': 0,
            'passed': 0
        }

        for ticker, info in ticker_info.items():
            # Skip invalid entries
            if info is None:
                continue

            market_cap = info.get('market_cap', 0) or 0
            price = info.get('current_price', 0) or 0
            volume = info.get('average_volume', 0) or 0
            quote_type = info.get('quote_type', '')

            # Apply filters
            if market_cap < self.min_market_cap:
                filter_stats['excluded_market_cap'] += 1
                logger.debug(f"{ticker}: Market cap ${market_cap:,.0f} below minimum")
                continue

            if price < self.min_price:
                filter_stats['excluded_price'] += 1
                logger.debug(f"{ticker}: Price ${price:.2f} below minimum")
                continue

            if volume < self.min_volume:
                filter_stats['excluded_volume'] += 1
                logger.debug(f"{ticker}: Volume {volume:,.0f} below minimum")
                continue

            # Exclude certain security types
            if quote_type in self.exclude_types:
                filter_stats['excluded_type'] += 1
                logger.debug(f"{ticker}: Excluded type {quote_type}")
                continue

            filter_stats['passed'] += 1
            filtered.append({
                'ticker': ticker,
                'exchange': info.get('exchange', 'Unknown'),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': market_cap,
                'price': price,
                'volume': volume
            })

        # Sort by market cap descending
        filtered.sort(key=lambda x: x['market_cap'], reverse=True)

        # Log filter summary
        logger.info("=" * 60)
        logger.info("FILTER SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total checked:         {filter_stats['total_checked']:>6,}")
        logger.info(f"Excluded (market cap): {filter_stats['excluded_market_cap']:>6,} (< ${self.min_market_cap:,.0f})")
        logger.info(f"Excluded (price):      {filter_stats['excluded_price']:>6,} (< ${self.min_price:.2f})")
        logger.info(f"Excluded (volume):     {filter_stats['excluded_volume']:>6,} (< {self.min_volume:,})")
        logger.info(f"Excluded (type):       {filter_stats['excluded_type']:>6,} ({', '.join(self.exclude_types)})")
        logger.info("-" * 60)
        logger.info(f"Passed filters:        {filter_stats['passed']:>6,}")
        logger.info("=" * 60)

        return {
            'tickers': filtered,
            'filter_stats': filter_stats
        }

    def fetch_all_tickers(self) -> dict:
        """
        Fetch tickers from all sources and remove duplicates.

        Returns:
            Dictionary with 'tickers' (set) and 'stats' (dict)
        """
        stats = {
            'sp500': 0,
            'nasdaq': 0,
            'nyse': 0,
            'russell3000': 0,
            'raw_total': 0,
            'unique_total': 0
        }

        all_tickers = set()

        # Fetch from each source
        sp500 = self.fetch_sp500()
        stats['sp500'] = len(sp500)
        all_tickers.update(sp500)

        nasdaq = self.fetch_nasdaq_composite()
        stats['nasdaq'] = len(nasdaq)
        all_tickers.update(nasdaq)

        nyse = self.fetch_nyse_listed()
        stats['nyse'] = len(nyse)
        all_tickers.update(nyse)

        russell3000 = self.fetch_russell3000_proxy()
        stats['russell3000'] = len(russell3000)
        all_tickers.update(russell3000)

        stats['raw_total'] = stats['sp500'] + stats['nasdaq'] + stats['nyse'] + stats['russell3000']
        stats['unique_total'] = len(all_tickers)

        # Clean up tickers
        cleaned = set()
        for ticker in all_tickers:
            if isinstance(ticker, str):
                ticker = ticker.strip().upper()
                # Skip tickers with problematic characters
                if ticker and not any(c in ticker for c in ['$', '^', ' ', '/']):
                    cleaned.add(ticker)

        duplicates_removed = len(all_tickers) - len(cleaned)

        # Apply ticker normalization to filter invalid formats
        # This removes warrants (.W), units (.U), preferred (.P), class shares (.A, -A, etc.)
        # BEFORE calling Yahoo Finance API, significantly reducing API failures
        before_normalization = len(cleaned)
        normalized = normalize_tickers(list(cleaned))
        normalized_set = set(normalized)
        excluded_by_normalization = before_normalization - len(normalized_set)

        # Update stats
        stats['normalized_total'] = len(normalized_set)
        stats['excluded_by_normalization'] = excluded_by_normalization

        # Update cleaned to use normalized tickers
        cleaned = normalized_set

        logger.info("=" * 60)
        logger.info("SOURCE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"S&P 500:        {stats['sp500']:>6,} tickers")
        logger.info(f"NASDAQ:         {stats['nasdaq']:>6,} tickers")
        logger.info(f"NYSE:           {stats['nyse']:>6,} tickers")
        logger.info(f"Russell 3000:   {stats['russell3000']:>6,} tickers")
        logger.info("-" * 60)
        logger.info(f"Raw Total:      {stats['raw_total']:>6,} tickers")
        logger.info(f"After dedup:    {stats['unique_total']:>6,} unique tickers")
        logger.info(f"After cleanup:  {before_normalization:>6,} valid tickers")
        if duplicates_removed > 0:
            logger.info(f"Removed:        {duplicates_removed:>6,} invalid/duplicate tickers")
        logger.info("-" * 60)
        logger.info("NORMALIZATION (warrants, units, preferred, class shares)")
        logger.info(f"Before:         {before_normalization:>6,} tickers")
        logger.info(f"Excluded:       {excluded_by_normalization:>6,} invalid formats")
        logger.info(f"After:          {stats['normalized_total']:>6,} normalized tickers")
        logger.info("=" * 60)

        return {
            'tickers': cleaned,
            'stats': stats
        }

    def run(self, output_path: Optional[str] = None) -> pd.DataFrame:
        """
        Run the complete ticker update process.

        Args:
            output_path: Path to save the CSV file

        Returns:
            DataFrame with filtered tickers
        """
        logger.info("=" * 60)
        logger.info("Extended Ticker Update - Starting")
        logger.info("=" * 60)

        # Fetch all tickers
        fetch_result = self.fetch_all_tickers()
        all_tickers = fetch_result['tickers']
        source_stats = fetch_result['stats']

        # Get info for all tickers
        logger.info("")
        logger.info("Fetching ticker information (this may take a while)...")
        ticker_list = list(all_tickers)

        # Process in batches to avoid memory issues
        batch_size = 500
        all_info = {}
        info_success_total = 0
        info_failed_total = 0

        for i in range(0, len(ticker_list), batch_size):
            batch = ticker_list[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(ticker_list) + batch_size - 1) // batch_size
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} tickers)...")
            batch_result = self.get_ticker_info_batch(batch, max_workers=4)
            all_info.update(batch_result['info'])
            info_success_total += batch_result['stats']['success']
            info_failed_total += batch_result['stats']['failed']

        logger.info("")
        logger.info("=" * 60)
        logger.info("INFO FETCH SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Attempted:   {len(ticker_list):>6,}")
        logger.info(f"Succeeded:   {info_success_total:>6,}")
        logger.info(f"Failed:      {info_failed_total:>6,}")
        logger.info("=" * 60)

        # Filter tickers
        logger.info("")
        filter_result = self.filter_tickers(all_info)
        filtered = filter_result['tickers']
        filter_stats = filter_result['filter_stats']

        # Limit to max_tickers
        before_limit = len(filtered)
        if len(filtered) > self.max_tickers:
            logger.info(f"\nLimiting to top {self.max_tickers} tickers by market cap")
            filtered = filtered[:self.max_tickers]
            logger.info(f"Reduced from {before_limit:,} to {len(filtered):,} tickers")

        # Create DataFrame
        output_columns = ['ticker', 'exchange', 'sector']
        if filtered:
            df = pd.DataFrame(filtered)
            df_output = df[output_columns]
        else:
            # Handle empty result: create DataFrame with required columns only
            df_output = pd.DataFrame(columns=output_columns)

        # Save to CSV
        if output_path is None:
            output_path = Path(__file__).parent.parent / "config" / "tickers.csv"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_output.to_csv(output_path, index=False)

        # Final Summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Sources fetched → Unique → Info success → Passed filters → Saved")
        logger.info(
            f"{source_stats['raw_total']:>6,} → "
            f"{source_stats['unique_total']:>6,} → "
            f"{info_success_total:>6,} → "
            f"{filter_stats['passed']:>6,} → "
            f"{len(df_output):>6,}"
        )
        logger.info("=" * 80)
        logger.info(f"Output file: {output_path}")
        logger.info("=" * 80)

        # Print sector distribution
        if 'sector' in df_output.columns:
            print("\nSector Distribution:")
            print("-" * 40)
            sector_counts = df_output['sector'].value_counts()
            for sector, count in sector_counts.items():
                print(f"{sector}: {count}")

        return df_output


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Update ticker list with extended coverage (3,500+ tickers)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output CSV path (default: config/tickers.csv)'
    )
    parser.add_argument(
        '--min-market-cap',
        type=float,
        default=2_000_000_000,
        help='Minimum market cap in USD (default: 2B)'
    )
    parser.add_argument(
        '--min-price',
        type=float,
        default=5.0,
        help='Minimum stock price (default: $5)'
    )
    parser.add_argument(
        '--min-volume',
        type=int,
        default=500_000,
        help='Minimum average daily volume (default: 500K)'
    )
    parser.add_argument(
        '--max-tickers',
        type=int,
        default=3500,
        help='Maximum number of tickers (default: 3500)'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )

    args = parser.parse_args()

    # Setup logger
    setup_logger(log_level=args.log_level)

    # Create fetcher and run
    fetcher = TickerFetcher(
        min_market_cap=args.min_market_cap,
        min_price=args.min_price,
        min_volume=args.min_volume,
        max_tickers=args.max_tickers
    )

    fetcher.run(output_path=args.output)


if __name__ == "__main__":
    main()
