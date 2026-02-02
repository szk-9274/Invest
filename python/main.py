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
        tickers: List of ticker symbols (from tickers.csv)
        args: Command line arguments
    """
    logger.info("=" * 60)
    logger.info("BACKTEST MODE")
    logger.info("=" * 60)

    # Override dates if provided
    start_date = args.start if args.start else config['backtest']['start_date']
    end_date = args.end if args.end else config['backtest']['end_date']

    use_benchmark = not args.no_benchmark

    # ========== STAGE2 RESULT CONNECTION ==========
    # CRITICAL: Load Stage2 screening results if available
    # Without this, backtest runs on ALL tickers (ignoring Stage2 filter)
    screening_results_path = Path(__file__).parent / config['output']['csv_path']
    stage2_filtered_tickers = None

    if screening_results_path.exists():
        try:
            screening_df = pd.read_csv(screening_results_path)
            if not screening_df.empty and 'ticker' in screening_df.columns:
                stage2_filtered_tickers = screening_df['ticker'].tolist()
                logger.info("=" * 60)
                logger.info("STAGE2 FILTER APPLIED")
                logger.info("=" * 60)
                logger.info(f"Stage2 results loaded from: {screening_results_path}")
                logger.info(f"Backtest universe: {len(tickers)} → {len(stage2_filtered_tickers)} tickers (Stage2 filtered)")
                logger.info(f"Stage2 candidates: {', '.join(stage2_filtered_tickers[:10])}" +
                           (f" ... and {len(stage2_filtered_tickers)-10} more" if len(stage2_filtered_tickers) > 10 else ""))

                # Use Stage2 filtered tickers for backtest
                tickers = stage2_filtered_tickers
            else:
                logger.warning("Stage2 results file is empty or missing 'ticker' column")
        except Exception as e:
            logger.warning(f"Failed to load Stage2 results: {e}")

    if stage2_filtered_tickers is None:
        logger.warning("=" * 60)
        logger.warning("NO STAGE2 FILTER - Using all tickers")
        logger.warning("=" * 60)
        logger.warning(f"Stage2 results not found at: {screening_results_path}")
        logger.warning("Backtest will run on ALL input tickers (may result in 0 trades)")
        logger.warning("RECOMMENDATION: Run 'python main.py --mode stage2' first")
        logger.warning("=" * 60)
    # ============================================

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


def explain_stage2(ticker: str, config: dict, use_benchmark: bool, target_date: str = None):
    """
    Explain Stage 2 detection results for a specific ticker.

    Args:
        ticker: Ticker symbol to analyze
        config: Configuration dictionary
        use_benchmark: Whether to use benchmark for RS calculation
        target_date: Optional date to analyze (YYYY-MM-DD)
    """
    from data.fetcher import YahooFinanceFetcher
    from analysis.stage_detector import StageDetector
    from analysis.indicators import calculate_all_indicators

    print("\n" + "=" * 80)
    print(f"STAGE 2 ANALYSIS: {ticker}")
    print("=" * 80)

    fetcher = YahooFinanceFetcher(request_delay=config['performance']['request_delay'])
    stage_detector = StageDetector(config['stage'])

    # Fetch stock data
    data = fetcher.fetch_data(ticker, period=config['data']['history_period'])
    if data is None:
        print(f"✗ Failed to fetch data for {ticker}")
        return

    print(f"✓ Data fetched: {len(data)} bars")

    if len(data) < 252:
        print(f"✗ Insufficient data: {len(data)} bars (need at least 252)")
        return

    # Fetch benchmark if needed
    benchmark_data = None
    if use_benchmark:
        benchmark_data = fetcher.fetch_benchmark('SPY', period=config['data']['history_period'])
        if benchmark_data is None:
            print("⚠ Benchmark fetch failed, switching to no-benchmark mode")
            use_benchmark = False
        else:
            print(f"✓ Benchmark fetched: {len(benchmark_data)} bars")

    if not use_benchmark:
        print("ℹ Running in NO-BENCHMARK mode (RS condition auto-passed)")

    # Calculate indicators
    data = calculate_all_indicators(data, benchmark_data)

    # Filter to target date if specified
    if target_date:
        target_ts = pd.Timestamp(target_date)
        if target_ts not in data.index:
            print(f"✗ Date {target_date} not found in data (available: {data.index[0].date()} to {data.index[-1].date()})")
            return
        data = data[data.index <= target_ts]
        print(f"✓ Analyzing as of {target_date}")

    # Get latest row
    latest = data.iloc[-1]
    analysis_date = latest.name.date() if hasattr(latest.name, 'date') else latest.name

    # Detect stage
    rs_line = data['rs_line'] if use_benchmark else None
    stage_result = stage_detector.detect_stage(data, rs_line, use_benchmark=use_benchmark)

    print("\n" + "-" * 80)
    print("STAGE DETECTION RESULT")
    print("-" * 80)
    print(f"Stage:           {stage_result['stage']}")
    print(f"Meets criteria:  {'YES' if stage_result['meets_criteria'] else 'NO'}")
    print(f"Analysis date:   {analysis_date}")

    # Get 52-week high/low
    lookback = min(252, len(data))
    high_52w = data['high'].tail(lookback).max()
    low_52w = data['low'].tail(lookback).min()

    # Calculate distances
    distance_from_high_pct = (high_52w - latest['close']) / high_52w * 100
    distance_from_low_pct = (latest['close'] - low_52w) / low_52w * 100

    print("\n" + "-" * 80)
    print("PRICE INFORMATION")
    print("-" * 80)
    print(f"Current price:        ${latest['close']:.2f}")
    print(f"52-week high:         ${high_52w:.2f}")
    print(f"52-week low:          ${low_52w:.2f}")
    print(f"Distance from high:   {distance_from_high_pct:.1f}%")
    print(f"Distance from low:    +{distance_from_low_pct:.1f}%")
    print(f"SMA 50:               ${latest['sma_50']:.2f}")
    print(f"SMA 150:              ${latest['sma_150']:.2f}")
    print(f"SMA 200:              ${latest['sma_200']:.2f}")
    print(f"Volume (50-day avg):  {latest['volume_ma_50']:,.0f}")

    # RS information
    if use_benchmark and 'rs_line' in data.columns:
        rs_line_clean = data['rs_line'].dropna()
        if len(rs_line_clean) >= 252:
            rs_52w_high = rs_line_clean.tail(252).max()
            rs_current = rs_line_clean.iloc[-1]
            rs_distance = (rs_current / rs_52w_high - 1) * 100
            print(f"\nRS Line (current):    {rs_current:.2f}")
            print(f"RS Line (52w high):   {rs_52w_high:.2f}")
            print(f"RS vs 52w high:       {rs_distance:+.1f}%")
            print(f"RS valid data points: {len(rs_line_clean)}/{len(data)}")
        else:
            print(f"\n⚠ RS Line has insufficient valid data: {len(rs_line_clean)}/252")

    # Condition details
    print("\n" + "-" * 80)
    print("STAGE 2 CONDITIONS (PASS/FAIL)")
    print("-" * 80)

    conditions = stage_result['details']
    params = config['stage']

    # Define condition explanations
    explanations = {
        'price_above_sma50': (
            f"Price > SMA(50)",
            f"${latest['close']:.2f} > ${latest['sma_50']:.2f}"
        ),
        'sma50_above_sma150': (
            f"SMA(50) > SMA(150)",
            f"${latest['sma_50']:.2f} > ${latest['sma_150']:.2f}"
        ),
        'sma150_above_sma200': (
            f"SMA(150) > SMA(200)",
            f"${latest['sma_150']:.2f} > ${latest['sma_200']:.2f}"
        ),
        'ma200_uptrend': (
            f"SMA(200) in uptrend",
            "slope > 0"
        ),
        'above_52w_low': (
            f"Price > {params['min_price_above_52w_low']:.0%} of 52w low",
            f"${latest['close']:.2f} >= ${low_52w * params['min_price_above_52w_low']:.2f}"
        ),
        'near_52w_high': (
            f"Price within {100 * (1 - params['max_distance_from_52w_high']):.0f}% of 52w high",
            f"${latest['close']:.2f} >= ${high_52w * params['max_distance_from_52w_high']:.2f}"
        ),
        'ma50_above_ma150_200': (
            f"SMA(50) > both SMA(150) and SMA(200)",
            f"${latest['sma_50']:.2f} > ${latest['sma_150']:.2f} and ${latest['sma_200']:.2f}"
        ),
        'rs_new_high': (
            f"RS Line near 52w high (auto-pass if no benchmark)",
            "RS >= 95% of 52w high" if use_benchmark else "auto-pass (no benchmark)"
        ),
        'sufficient_volume': (
            f"Volume >= {params.get('min_volume', 500_000):,}",
            f"{latest['volume_ma_50']:,.0f} >= {params.get('min_volume', 500_000):,}"
        )
    }

    for cond_name, passed in conditions.items():
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        title, detail = explanations.get(cond_name, (cond_name, ""))
        print(f"{symbol} [{status:4}] {title}")
        print(f"          {detail}")

    print("=" * 80)

    if stage_result['meets_criteria']:
        print(f"\n✓ {ticker} PASSES Stage 2 detection")
    else:
        failed_conditions = [k for k, v in conditions.items() if not v]
        print(f"\n✗ {ticker} FAILS Stage 2 detection")
        print(f"  Failed conditions: {', '.join(failed_conditions)}")

    print()


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
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    parser.add_argument(
        '--diagnose',
        action='store_true',
        help='Enable diagnostic mode (shows detailed backtest analysis)'
    )
    parser.add_argument(
        '--explain-stage2',
        type=str,
        metavar='TICKER',
        help='Explain why a ticker passes or fails Stage 2 conditions'
    )
    parser.add_argument(
        '--date',
        type=str,
        metavar='YYYY-MM-DD',
        help='Date for --explain-stage2 analysis (default: latest)'
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
    log_level = 'DEBUG' if args.verbose else config['output']['log_level']
    setup_logger(
        log_path=config['output']['log_path'],
        log_level=log_level
    )

    # Handle explain-stage2 mode
    if args.explain_stage2:
        use_benchmark = not args.no_benchmark
        explain_stage2(args.explain_stage2, config, use_benchmark, args.date)
        return

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
