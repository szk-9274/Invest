"""
Stock Screening System - Main Entry Point
Based on Minervini's Stage Theory
(VCP Pattern detection temporarily disabled for validation)
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
from backtest.engine import BacktestEngine, print_backtest_report
from backtest.performance import calculate_cagr

try:
    from backtest.visualization import visualize_backtest_results
    VISUALIZATION_AVAILABLE = visualize_backtest_results is not None
except (ImportError, AttributeError, Exception):
    VISUALIZATION_AVAILABLE = False


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


def run_backtest_mode(config: dict, tickers: list, args):
    """
    Run backtest mode.

    Args:
        config: Configuration dictionary
        tickers: List of ticker symbols
        args: Command line arguments
    """
    logger.info("=" * 60)
    logger.info("BACKTEST MODE")
    logger.info("=" * 60)

    # Override dates if provided
    start_date = args.start if args.start else config['backtest']['start_date']
    end_date = args.end if args.end else config['backtest']['end_date']

    use_benchmark = not args.no_benchmark

    logger.info(f"Period: {start_date} to {end_date}")
    logger.info(f"Tickers: {len(tickers)}")
    logger.info(f"Benchmark: {'Enabled' if use_benchmark else 'Disabled'}")

    # Initialize and run backtest engine
    engine = BacktestEngine(config, use_benchmark=use_benchmark)
    result = engine.run(tickers, start_date, end_date)

    # Print report
    print_backtest_report(result)

    # Calculate and display CAGR
    if result.total_trades > 0:
        years = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days / 365.25
        cagr = calculate_cagr(
            result.initial_capital,
            result.final_capital,
            years
        )
        print(f"CAGR:                 {cagr:.1%}")

    # Visualize results
    output_dir = Path(__file__).parent / "output" / "backtest"
    output_dir.mkdir(parents=True, exist_ok=True)

    if VISUALIZATION_AVAILABLE:
        try:
            visualize_backtest_results(result, output_dir)
            logger.info(f"Charts saved to: {output_dir}")
        except Exception as e:
            logger.warning(f"Could not generate charts: {e}")
    else:
        logger.warning("matplotlib not available, skipping chart generation")

    # Save trade details
    if result.trades:
        trades_df = pd.DataFrame([
            {
                'ticker': t.ticker,
                'entry_date': t.entry_date.strftime('%Y-%m-%d') if t.entry_date else None,
                'entry_price': round(t.entry_price, 2),
                'exit_date': t.exit_date.strftime('%Y-%m-%d') if t.exit_date else None,
                'exit_price': round(t.exit_price, 2) if t.exit_price else None,
                'exit_reason': t.exit_reason,
                'shares': t.shares,
                'pnl': round(t.pnl, 2),
                'pnl_pct': round(t.pnl_pct * 100, 2)
            }
            for t in result.trades
        ])
        trades_file = output_dir / "trades.csv"
        trades_df.to_csv(trades_file, index=False)
        logger.info(f"Trade details saved to: {trades_file}")


def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Stock Screening System based on Minervini Stage Theory'
    )
    parser.add_argument(
        '--mode',
        choices=['full', 'stage2', 'test', 'backtest'],
        default='full',
        help='Mode: full (Stage2 only, VCP disabled), stage2 (Stage2 only), test (quick test), backtest (backtest engine)'
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
    parser.add_argument(
        '--with-fundamentals',
        action='store_true',
        help='Apply fundamentals filter (EPS/Revenue growth, QoQ acceleration)'
    )
    parser.add_argument(
        '--start',
        type=str,
        help='Backtest start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end',
        type=str,
        help='Backtest end date (YYYY-MM-DD)'
    )

    # Benchmark options (mutually exclusive)
    benchmark_group = parser.add_mutually_exclusive_group()
    benchmark_group.add_argument(
        '--use-benchmark',
        action='store_true',
        default=True,
        dest='use_benchmark',
        help='Use SPY benchmark for relative strength calculation (default)'
    )
    benchmark_group.add_argument(
        '--no-benchmark',
        action='store_true',
        default=False,
        help='Disable SPY benchmark; use only technical conditions for Stage 2'
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
    logger.info(f"Benchmark: {'Disabled' if args.no_benchmark else 'Enabled'}")
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

    # Run backtest mode
    if args.mode == 'backtest':
        run_backtest_mode(config, tickers, args)
        return

    # Determine benchmark usage
    use_benchmark = not args.no_benchmark

    # Initialize screener
    screener = Screener(config, use_benchmark=use_benchmark)

    # Run screening
    if args.mode == 'full' or args.mode == 'test':
        results = screener.screen(tickers)
    elif args.with_fundamentals:
        results = screener.screen_with_fundamentals(tickers)
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
    if not use_benchmark:
        print("Benchmark: Disabled (RS condition auto-passed)")
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
