"""
Stock Screening System - Main Entry Point
Based on Minervini's Stage Theory and VCP Pattern
"""
import yaml
import pandas as pd
from pathlib import Path
from loguru import logger
import argparse
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from screening.screener import Screener
from utils.logger import setup_logger


def load_config(config_path: str = "config/params.yaml") -> dict:
    """Load configuration file"""
    config_file = Path(__file__).parent / config_path
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_tickers(tickers_path: str = "config/tickers.csv") -> list:
    """Load ticker list"""
    tickers_file = Path(__file__).parent / tickers_path
    df = pd.read_csv(tickers_file)
    return df['ticker'].tolist()


def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Stock Screening System based on Minervini Stage Theory'
    )
    parser.add_argument(
        '--mode',
        choices=['full', 'stage2', 'test'],
        default='full',
        help='Screening mode: full (Stage2+VCP), stage2 (Stage2 only), test (quick test)'
    )
    parser.add_argument(
        '--tickers',
        type=str,
        help='Comma-separated list of tickers to screen (overrides config)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output CSV path (overrides config)'
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Setup logger
    setup_logger(
        log_path=config['output']['log_path'],
        log_level=config['output']['log_level']
    )

    logger.info("=" * 60)
    logger.info("Stock Screening System Started")
    logger.info(f"Mode: {args.mode}")
    logger.info("=" * 60)

    # Load tickers
    if args.tickers:
        tickers = [t.strip() for t in args.tickers.split(',')]
    elif args.mode == 'test':
        # Quick test with a few tickers
        tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META']
    else:
        tickers = load_tickers()

    logger.info(f"Loaded {len(tickers)} tickers")

    # Initialize screener
    screener = Screener(config)

    # Run screening
    if args.mode == 'full' or args.mode == 'test':
        results = screener.screen(tickers)
    else:  # stage2
        results = screener.screen_stage2_only(tickers)

    if results.empty:
        logger.warning("No candidates found")
        print("\n" + "=" * 60)
        print("NO CANDIDATES FOUND")
        print("=" * 60)
        return

    # Sort results by risk/reward (descending)
    if 'risk_reward' in results.columns:
        results = results.sort_values('risk_reward', ascending=False)
    elif 'distance_from_high_pct' in results.columns:
        results = results.sort_values('distance_from_high_pct', ascending=True)

    # Save to CSV
    output_path = args.output if args.output else config['output']['csv_path']
    output_file = Path(__file__).parent / output_path
    output_file.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_file, index=False)

    logger.info(f"Results saved to: {output_file}")
    logger.info(f"Total candidates: {len(results)}")

    # Display summary
    print("\n" + "=" * 80)
    print(f"SCREENING RESULTS ({len(results)} candidates)")
    print("=" * 80)

    # Show top 10 results
    display_cols = results.columns.tolist()
    if len(results) > 10:
        print(results.head(10).to_string(index=False))
        print(f"\n... and {len(results) - 10} more candidates")
    else:
        print(results.to_string(index=False))

    print("=" * 80)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
