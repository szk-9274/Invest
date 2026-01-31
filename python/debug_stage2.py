"""
Debug script to analyze Stage 2 detection for specific tickers
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import yaml
import pandas as pd
from loguru import logger

from data.fetcher import YahooFinanceFetcher
from analysis.stage_detector import StageDetector
from analysis.indicators import calculate_all_indicators

def load_config(config_path: str = "config/params.yaml") -> dict:
    """Load configuration file"""
    config_file = Path(__file__).parent / config_path
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def debug_ticker(ticker: str, config: dict):
    """Debug Stage 2 detection for a specific ticker"""
    print(f"\n{'='*60}")
    print(f"Debugging: {ticker}")
    print(f"{'='*60}")

    fetcher = YahooFinanceFetcher(request_delay=config['performance']['request_delay'])

    # Fetch data
    data = fetcher.fetch_data(ticker, period=config['data']['history_period'])
    if data is None:
        print(f"[FAIL] Failed to fetch data")
        return

    print(f"[OK] Data fetched: {len(data)} bars")

    if len(data) < 252:
        print(f"[FAIL] Insufficient data: {len(data)} < 252")
        return

    # Fetch benchmark
    benchmark_data = fetcher.fetch_benchmark('SPY', period=config['data']['history_period'])
    if benchmark_data is None:
        print(f"[WARN] Benchmark not available, using no-benchmark mode")
        use_benchmark = False
    else:
        use_benchmark = True
        print(f"[OK] Benchmark fetched: {len(benchmark_data)} bars")

    # Calculate indicators
    data = calculate_all_indicators(data, benchmark_data)

    # Detect stage
    stage_detector = StageDetector(config['stage'])
    rs_line = data['rs_line'] if use_benchmark else None
    stage_result = stage_detector.detect_stage(data, rs_line, use_benchmark=use_benchmark)

    print(f"\nStage Detection:")
    print(f"  Stage: {stage_result['stage']}")
    print(f"  Meets criteria: {stage_result['meets_criteria']}")
    print(f"\nCondition Details:")
    for condition, value in stage_result['details'].items():
        status = "PASS" if value else "FAIL"
        print(f"  [{status}] {condition}: {value}")

    if stage_result['stage'] != 2:
        print(f"\n[FAIL] Not Stage 2 (Stage {stage_result['stage']})")
        return

    # Current state
    current_price = data['close'].iloc[-1]
    high_52w = data['high'].tail(252).max()
    low_52w = data['low'].tail(252).min()
    distance_from_high = (high_52w - current_price) / high_52w * 100

    print(f"\nPrice Info:")
    print(f"  Current: ${current_price:.2f}")
    print(f"  52W High: ${high_52w:.2f}")
    print(f"  52W Low: ${low_52w:.2f}")
    print(f"  Distance from High: {distance_from_high:.1f}%")

    print(f"\n[OK] Passes Stage 2 Detection")

if __name__ == "__main__":
    config = load_config()

    # Test tickers
    test_tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META', 'TSLA', 'AMZN']

    for ticker in test_tickers:
        try:
            debug_ticker(ticker, config)
        except Exception as e:
            print(f"Error: {e}")

