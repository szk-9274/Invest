"""
Extended Ticker List Update Script
Fetches approximately 3,500 tickers from S&P 500, NASDAQ, and Russell 3000
"""
import pandas as pd
import warnings

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
            tables = pd.read_html(url)
            df = tables[0]
            tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
            logger.info(f"Fetched {len(tickers)} S&P 500 tickers")
            return tickers
        except Exception as e:
            logger.error(f"Failed to fetch S&P 500: {e}")
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
            logger.info(f"Fetched {len(tickers)} NASDAQ tickers")
            return tickers
        except Exception as e:
            logger.error(f"Failed to fetch NASDAQ composite: {e}")
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
            logger.info(f"Fetched {len(tickers)} NYSE tickers")
            return tickers
        except Exception as e:
            logger.error(f"Failed to fetch NYSE tickers: {e}")
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
                logger.info(f"Fetched {len(tickers)} Russell 3000 tickers from IWV")
                return tickers
        except Exception as e:
            logger.warning(f"Could not fetch IWV holdings: {e}")

        # Fallback: return empty list, will rely on other sources
        logger.warning("Using NASDAQ + NYSE as Russell 3000 proxy")
        return []

    def get_ticker_info_batch(
        self,
        tickers: List[str],
        max_workers: int = 4
    ) -> Dict[str, Dict]:
        """
        Get ticker info for multiple symbols in parallel.

        Args:
            tickers: List of ticker symbols
            max_workers: Number of parallel workers

        Returns:
            Dictionary {ticker: info_dict}
        """
        results = {}

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
                logger.debug(f"{ticker}: Error fetching info - {e}")
                return ticker, None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_single, t): t for t in tickers}

            for future in tqdm(as_completed(futures), total=len(tickers), desc="Fetching info"):
                ticker, info = future.result()
                if info is not None:
                    results[ticker] = info

        return results

    def filter_tickers(self, ticker_info: Dict[str, Dict]) -> List[Dict]:
        """
        Filter tickers based on criteria.

        Args:
            ticker_info: Dictionary of ticker info

        Returns:
            List of filtered ticker dictionaries
        """
        filtered = []

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
                logger.debug(f"{ticker}: Market cap ${market_cap:,.0f} below minimum")
                continue

            if price < self.min_price:
                logger.debug(f"{ticker}: Price ${price:.2f} below minimum")
                continue

            if volume < self.min_volume:
                logger.debug(f"{ticker}: Volume {volume:,.0f} below minimum")
                continue

            # Exclude certain security types
            if quote_type in self.exclude_types:
                logger.debug(f"{ticker}: Excluded type {quote_type}")
                continue

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

        logger.info(f"Filtered to {len(filtered)} tickers meeting criteria")
        return filtered

    def fetch_all_tickers(self) -> Set[str]:
        """
        Fetch tickers from all sources and remove duplicates.

        Returns:
            Set of unique ticker symbols
        """
        all_tickers = set()

        # Fetch from each source
        sp500 = self.fetch_sp500()
        all_tickers.update(sp500)

        nasdaq = self.fetch_nasdaq_composite()
        all_tickers.update(nasdaq)

        nyse = self.fetch_nyse_listed()
        all_tickers.update(nyse)

        russell3000 = self.fetch_russell3000_proxy()
        all_tickers.update(russell3000)

        # Clean up tickers
        cleaned = set()
        for ticker in all_tickers:
            if isinstance(ticker, str):
                ticker = ticker.strip().upper()
                # Skip tickers with problematic characters
                if ticker and not any(c in ticker for c in ['$', '^', ' ', '/']):
                    cleaned.add(ticker)

        logger.info(f"Total unique tickers after deduplication: {len(cleaned)}")
        return cleaned

    def run(self, output_path: Optional[str] = None) -> pd.DataFrame:
        """
        Run the complete ticker update process.

        Args:
            output_path: Path to save the CSV file

        Returns:
            DataFrame with filtered tickers
        """
        logger.info("=" * 60)
        logger.info("Starting Extended Ticker Update")
        logger.info("=" * 60)

        # Fetch all tickers
        all_tickers = self.fetch_all_tickers()
        logger.info(f"Fetched {len(all_tickers)} unique tickers")

        # Get info for all tickers
        logger.info("Fetching ticker information (this may take a while)...")
        ticker_list = list(all_tickers)

        # Process in batches to avoid memory issues
        batch_size = 500
        all_info = {}

        for i in range(0, len(ticker_list), batch_size):
            batch = ticker_list[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} tickers)...")
            batch_info = self.get_ticker_info_batch(batch, max_workers=4)
            all_info.update(batch_info)

        # Filter tickers
        filtered = self.filter_tickers(all_info)

        # Limit to max_tickers
        if len(filtered) > self.max_tickers:
            logger.info(f"Limiting to top {self.max_tickers} tickers by market cap")
            filtered = filtered[:self.max_tickers]

        # Create DataFrame
        df = pd.DataFrame(filtered)

        # Select and reorder columns for output
        output_columns = ['ticker', 'exchange', 'sector']
        df_output = df[output_columns]

        # Save to CSV
        if output_path is None:
            output_path = Path(__file__).parent.parent / "config" / "tickers.csv"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_output.to_csv(output_path, index=False)

        logger.info("=" * 60)
        logger.info(f"Update Complete!")
        logger.info(f"Total tickers saved: {len(df_output)}")
        logger.info(f"Output file: {output_path}")
        logger.info("=" * 60)

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
