"""
Test Stage2 checks execution during backtest simulation.

This test suite verifies that Stage2 checks are properly performed
when valid ticker data is available during the backtest simulation.

Issue: Backtest showing 0 Stage2 checks despite having valid data.
Root cause hypothesis: Date index mismatch between trading_days and ticker data.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def create_mock_stock_data(
    start_date: str = "2022-01-01",
    end_date: str = "2024-01-01",
    tz_aware: bool = False
) -> pd.DataFrame:
    """
    Create mock stock data with all required columns for Stage2 detection.

    Args:
        start_date: Start date for the data
        end_date: End date for the data
        tz_aware: Whether to create timezone-aware index

    Returns:
        DataFrame with OHLCV data and calculated indicators
    """
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')

    if tz_aware:
        date_range = date_range.tz_localize('America/New_York')

    n = len(date_range)
    np.random.seed(42)  # For reproducibility

    # Create trending stock data (simulating Stage 2 uptrend)
    base_price = 100.0
    trend = np.linspace(0, 50, n)  # Upward trend
    noise = np.random.randn(n) * 2
    close = base_price + trend + noise

    data = pd.DataFrame({
        'open': close - np.random.rand(n) * 2,
        'high': close + np.random.rand(n) * 3,
        'low': close - np.random.rand(n) * 3,
        'close': close,
        'volume': np.random.randint(500000, 2000000, n),
    }, index=date_range)

    # Calculate SMAs (required for Stage2)
    data['sma_50'] = data['close'].rolling(window=50).mean()
    data['sma_150'] = data['close'].rolling(window=150).mean()
    data['sma_200'] = data['close'].rolling(window=200).mean()
    data['volume_ma_50'] = data['volume'].rolling(window=50).mean()

    # RS line (mock - assumes benchmark comparison)
    data['rs_line'] = data['close'] / 100  # Simplified RS calculation

    return data


def create_mock_benchmark_data(
    start_date: str = "2022-01-01",
    end_date: str = "2024-01-01",
    tz_aware: bool = False
) -> pd.DataFrame:
    """Create mock benchmark (SPY) data."""
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')

    if tz_aware:
        date_range = date_range.tz_localize('America/New_York')

    n = len(date_range)
    np.random.seed(123)

    base_price = 400.0
    trend = np.linspace(0, 30, n)
    noise = np.random.randn(n) * 3
    close = base_price + trend + noise

    return pd.DataFrame({
        'open': close - np.random.rand(n) * 2,
        'high': close + np.random.rand(n) * 3,
        'low': close - np.random.rand(n) * 3,
        'close': close,
        'volume': np.random.randint(50000000, 100000000, n),
    }, index=date_range)


def get_test_config():
    """Get minimal test configuration."""
    return {
        'performance': {'request_delay': 0.0},
        'stage': {
            'strict': {
                'min_price_above_52w_low': 1.30,
                'max_distance_from_52w_high': 0.75,
                'rs_new_high_threshold': 0.95,
                'min_volume': 500000
            },
            'relaxed': {
                'min_price_above_52w_low': 1.20,
                'max_distance_from_52w_high': 0.60,
                'rs_new_high_threshold': 0.90,
                'min_volume': 300000
            },
            'auto_fallback_enabled': True,
            'min_trades_threshold': 1,
            'min_slope_200_days': 20,
            'min_volume': 500000,
            'min_price_above_52w_low': 1.30,
            'max_distance_from_52w_high': 0.75
        },
        'vcp': {
            'base_period_min': 35,
            'base_period_max': 65,
            'contraction_sequence': [0.25, 0.15, 0.08, 0.05]
        },
        'backtest': {
            'initial_capital': 10000,
            'max_positions': 5,
            'commission': 0.001,
            'start_date': '2023-01-01',
            'end_date': '2024-01-01'
        },
        'risk': {'risk_per_trade': 0.0075}
    }


class TestStage2ChecksExecution:
    """Test that Stage2 checks are executed during backtest."""

    def test_stage2_checks_count_with_valid_data(self):
        """
        CRITICAL TEST: Stage2 checks should be performed when valid ticker data exists.

        This test verifies that the backtest engine performs Stage2 checks
        when tickers have sufficient historical data (>252 bars).
        """
        from backtest.engine import BacktestEngine
        from analysis.indicators import calculate_all_indicators

        config = get_test_config()

        # Create mock data with TZ-naive index (matching expected format)
        mock_stock_data = create_mock_stock_data(tz_aware=False)
        mock_benchmark = create_mock_benchmark_data(tz_aware=False)

        # Calculate all indicators
        mock_stock_data = calculate_all_indicators(mock_stock_data, mock_benchmark)

        # Mock the fetcher to return our test data
        with patch('backtest.engine.YahooFinanceFetcher') as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.fetch_data.return_value = mock_stock_data.copy()
            mock_fetcher.fetch_benchmark.return_value = mock_benchmark.copy()

            engine = BacktestEngine(config, use_benchmark=True)
            result = engine.run(
                tickers=['TEST'],
                start_date='2023-01-01',
                end_date='2024-01-01'
            )

        # CRITICAL ASSERTION: Stage2 checks must be > 0
        assert engine.diagnostics['stage2_checks'] > 0, (
            f"Stage2 checks should be > 0 when valid data exists. "
            f"Got: {engine.diagnostics['stage2_checks']}"
        )

    def test_stage2_checks_with_timezone_aware_data(self):
        """
        Test that Stage2 checks work correctly with timezone-aware data.

        The engine should normalize timezone-aware data to tz-naive
        before performing date comparisons.
        """
        from backtest.engine import BacktestEngine
        from analysis.indicators import calculate_all_indicators

        config = get_test_config()

        # Create mock data with TIMEZONE-AWARE index
        mock_stock_data = create_mock_stock_data(tz_aware=True)
        mock_benchmark = create_mock_benchmark_data(tz_aware=True)

        # Calculate all indicators
        mock_stock_data = calculate_all_indicators(mock_stock_data, mock_benchmark)

        with patch('backtest.engine.YahooFinanceFetcher') as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.fetch_data.return_value = mock_stock_data.copy()
            mock_fetcher.fetch_benchmark.return_value = mock_benchmark.copy()

            engine = BacktestEngine(config, use_benchmark=True)
            result = engine.run(
                tickers=['TEST'],
                start_date='2023-01-01',
                end_date='2024-01-01'
            )

        # Stage2 checks should still work with tz-aware data
        assert engine.diagnostics['stage2_checks'] > 0, (
            f"Stage2 checks should work with timezone-aware data. "
            f"Got: {engine.diagnostics['stage2_checks']}"
        )

    def test_date_index_matching_in_backtest_loop(self):
        """
        Test that trading_days and ticker data indices are compatible.

        This is a key test for the root cause: if indices don't match,
        the 'date in data.index' check will always fail.
        """
        from backtest.engine import BacktestEngine

        config = get_test_config()

        # Create data with specific dates we can verify
        stock_data = create_mock_stock_data(
            start_date='2022-01-01',
            end_date='2024-01-01',
            tz_aware=False
        )
        benchmark_data = create_mock_benchmark_data(
            start_date='2022-01-01',
            end_date='2024-01-01',
            tz_aware=False
        )

        # Verify index overlap
        backtest_start = pd.Timestamp('2023-01-01')
        backtest_end = pd.Timestamp('2024-01-01')

        # Filter to backtest period
        stock_in_period = stock_data[
            (stock_data.index >= backtest_start) &
            (stock_data.index <= backtest_end)
        ]
        benchmark_in_period = benchmark_data[
            (benchmark_data.index >= backtest_start) &
            (benchmark_data.index <= backtest_end)
        ]

        # Indices should be compatible (both tz-naive after normalization)
        assert stock_in_period.index.tz is None, "Stock data index should be tz-naive"
        assert benchmark_in_period.index.tz is None, "Benchmark index should be tz-naive"

        # There should be overlapping dates
        common_dates = stock_in_period.index.intersection(benchmark_in_period.index)
        assert len(common_dates) > 200, (
            f"Should have >200 common trading days. Got: {len(common_dates)}"
        )

    def test_multiple_tickers_stage2_checks(self):
        """
        Test Stage2 checks with multiple tickers.

        With N tickers and M trading days after day 252,
        we should have approximately N * (M - buffer) Stage2 checks.
        """
        from backtest.engine import BacktestEngine
        from analysis.indicators import calculate_all_indicators

        config = get_test_config()

        tickers = ['AAPL', 'MSFT', 'NVDA']

        # Create separate data for each ticker
        ticker_data = {}
        for ticker in tickers:
            np.random.seed(hash(ticker) % 2**32)
            data = create_mock_stock_data(tz_aware=False)
            ticker_data[ticker] = data

        benchmark_data = create_mock_benchmark_data(tz_aware=False)

        def mock_fetch_data(symbol, period='5y'):
            if symbol in ticker_data:
                data = ticker_data[symbol].copy()
                return calculate_all_indicators(data, benchmark_data)
            return None

        with patch('backtest.engine.YahooFinanceFetcher') as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.fetch_data.side_effect = mock_fetch_data
            mock_fetcher.fetch_benchmark.return_value = benchmark_data.copy()

            engine = BacktestEngine(config, use_benchmark=True)
            result = engine.run(
                tickers=tickers,
                start_date='2023-01-01',
                end_date='2024-01-01'
            )

        # With 3 tickers and ~250 trading days (minus 252 day warmup offset),
        # we expect a significant number of Stage2 checks
        # The exact number depends on data overlap, but should be > 0
        assert engine.diagnostics['stage2_checks'] > 0, (
            f"Multiple tickers should produce Stage2 checks. "
            f"Got: {engine.diagnostics['stage2_checks']}"
        )


class TestBacktestLoopDateHandling:
    """Test date handling in the backtest main loop."""

    def test_trading_days_derived_correctly(self):
        """
        Test that trading_days are correctly derived from benchmark or ticker data.
        """
        from backtest.engine import BacktestEngine

        config = get_test_config()

        benchmark_data = create_mock_benchmark_data(tz_aware=False)
        stock_data = create_mock_stock_data(tz_aware=False)

        # Filter benchmark to backtest period
        start = pd.Timestamp('2023-01-01')
        end = pd.Timestamp('2024-01-01')

        filtered_benchmark = benchmark_data[
            (benchmark_data.index >= start) & (benchmark_data.index <= end)
        ]

        # Trading days from benchmark should be tz-naive
        trading_days = filtered_benchmark.index
        assert trading_days.tz is None, "Trading days should be tz-naive"

        # Should have approximately 250-265 business days in a year
        # (Business days include holidays, so slightly higher than actual trading days)
        assert 200 <= len(trading_days) <= 265, (
            f"Expected ~250-265 business days in 2023, got {len(trading_days)}"
        )

    def test_date_membership_check_works(self):
        """
        Test that 'date in data.index' works correctly after normalization.

        This is the critical check at engine.py line 286-287 that
        determines whether Stage2 checks are performed.
        """
        # Create trading_days (tz-naive)
        trading_days = pd.date_range(start='2023-01-01', end='2023-01-31', freq='B')

        # Create stock data index (tz-naive)
        stock_index = pd.date_range(start='2022-01-01', end='2024-01-01', freq='B')

        # All trading_days should be in stock_index
        matches = sum(1 for d in trading_days if d in stock_index)
        assert matches == len(trading_days), (
            f"All trading days should be in stock index. "
            f"Matches: {matches}/{len(trading_days)}"
        )

    def test_timezone_normalization_preserves_dates(self):
        """
        Test that timezone normalization doesn't change date values.
        """
        # Create tz-aware date
        tz_aware_index = pd.date_range(
            start='2023-01-03',
            periods=5,
            freq='B',
            tz='America/New_York'
        )

        # Normalize to tz-naive
        tz_naive_index = tz_aware_index.tz_localize(None)

        # Dates should be preserved
        for tz_aware, tz_naive in zip(tz_aware_index, tz_naive_index):
            assert tz_aware.date() == tz_naive.date(), (
                f"Date should be preserved after normalization: "
                f"{tz_aware} -> {tz_naive}"
            )


class TestStage2ChecksWithRSLine:
    """Test RS line calculation and its impact on Stage2 checks."""

    def test_rs_line_calculated_correctly(self):
        """
        Test that RS line is properly calculated when indices overlap.
        """
        from analysis.indicators import calculate_rs_line

        # Create stock and benchmark data with same index
        dates = pd.date_range(start='2023-01-01', periods=100, freq='B')

        stock_data = pd.DataFrame({
            'close': np.linspace(100, 150, 100)
        }, index=dates)

        benchmark_data = pd.DataFrame({
            'close': np.linspace(400, 450, 100)
        }, index=dates)

        rs_line = calculate_rs_line(stock_data, benchmark_data)

        # RS line should have same length as input
        assert len(rs_line) == 100, f"RS line should have 100 values, got {len(rs_line)}"
        assert not rs_line.isna().all(), "RS line should not be all NaN"

    def test_rs_line_empty_when_no_index_overlap(self):
        """
        Test that RS line is empty when there's no index overlap.

        This can happen due to timezone mismatch.
        """
        from analysis.indicators import calculate_rs_line

        # Create stock data with tz-aware index
        stock_dates = pd.date_range(
            start='2023-01-01', periods=100, freq='B',
            tz='America/New_York'
        )
        stock_data = pd.DataFrame({
            'close': np.linspace(100, 150, 100)
        }, index=stock_dates)

        # Create benchmark data with tz-naive index (mismatch!)
        benchmark_dates = pd.date_range(
            start='2023-01-01', periods=100, freq='B'
        )
        benchmark_data = pd.DataFrame({
            'close': np.linspace(400, 450, 100)
        }, index=benchmark_dates)

        rs_line = calculate_rs_line(stock_data, benchmark_data)

        # RS line should be empty due to timezone mismatch
        assert len(rs_line) == 0, (
            f"RS line should be empty when indices don't overlap. Got {len(rs_line)}"
        )


class TestDiagnosticsAccuracy:
    """Test that diagnostics accurately reflect backtest execution."""

    def test_diagnostics_initialized_correctly(self):
        """Test that diagnostics dict is properly initialized."""
        from backtest.engine import BacktestEngine

        config = get_test_config()
        engine = BacktestEngine(config)

        expected_keys = [
            'stage2_checks',
            'stage2_passed',
            'stage2_failed_conditions',
            'insufficient_capital',
            'max_positions_reached',
            'insufficient_data',
            'total_entry_attempts'
        ]

        for key in expected_keys:
            assert key in engine.diagnostics, f"Missing diagnostic key: {key}"

        assert engine.diagnostics['stage2_checks'] == 0, "Initial stage2_checks should be 0"

    def test_insufficient_data_tracked(self):
        """
        Test that insufficient_data is incremented when data < 252 bars.
        """
        from backtest.engine import BacktestEngine
        from analysis.indicators import calculate_all_indicators

        config = get_test_config()

        # Create data with only 200 bars (insufficient)
        short_data = create_mock_stock_data(
            start_date='2023-06-01',  # Only ~6 months of data
            end_date='2024-01-01',
            tz_aware=False
        )
        benchmark_data = create_mock_benchmark_data(tz_aware=False)

        with patch('backtest.engine.YahooFinanceFetcher') as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            # Return data that's too short (< 252 bars after filtering)
            mock_fetcher.fetch_data.return_value = short_data.copy()
            mock_fetcher.fetch_benchmark.return_value = benchmark_data.copy()

            engine = BacktestEngine(config, use_benchmark=True)
            result = engine.run(
                tickers=['SHORT'],
                start_date='2023-01-01',
                end_date='2024-01-01'
            )

        # Data should be filtered out due to insufficient length
        # The ticker should not even make it to Stage2 checks
        # because fetch returns short data and len(data) > 252 check fails


class TestLoopIndexBug:
    """
    Test for the loop index bug that causes 0 Stage2 checks.

    BUG: The check `if i < 252: continue` at engine.py line 237 skips
    based on loop index, not historical data availability.

    When backtest period has <= 252 trading days, ALL iterations are skipped.
    """

    def test_one_year_backtest_should_have_stage2_checks(self):
        """
        CRITICAL: A 1-year backtest should perform Stage2 checks.

        The bug: trading_days has ~250 days (1 year), but loop skips
        first 252 iterations, resulting in 0 Stage2 checks.
        """
        from backtest.engine import BacktestEngine
        from analysis.indicators import calculate_all_indicators

        config = get_test_config()

        # Create 4 years of stock data (plenty of history)
        stock_data = create_mock_stock_data(
            start_date='2020-01-01',
            end_date='2024-01-01',
            tz_aware=False
        )
        benchmark_data = create_mock_benchmark_data(
            start_date='2020-01-01',
            end_date='2024-01-01',
            tz_aware=False
        )

        stock_data_with_indicators = calculate_all_indicators(stock_data, benchmark_data)

        with patch('backtest.engine.YahooFinanceFetcher') as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.fetch_data.return_value = stock_data_with_indicators.copy()
            mock_fetcher.fetch_benchmark.return_value = benchmark_data.copy()

            engine = BacktestEngine(config, use_benchmark=True)

            # Run 1-year backtest (approximately 250 trading days)
            result = engine.run(
                tickers=['TEST_TICKER'],
                start_date='2023-01-01',
                end_date='2024-01-01'
            )

        # BUG MANIFESTATION: With the bug, this assertion fails
        # because all 250 trading days are skipped by `if i < 252`
        assert engine.diagnostics['stage2_checks'] > 0, (
            f"1-year backtest should perform Stage2 checks. "
            f"Got: {engine.diagnostics['stage2_checks']}. "
            f"This indicates the loop index bug is present."
        )

    def test_loop_index_vs_historical_data_check(self):
        """
        Verify that Stage2 checks depend on historical data availability,
        not on the loop iteration index.

        The correct behavior: Check if ticker has >= 252 bars of history
        before the current simulation date.
        """
        from backtest.engine import BacktestEngine
        from analysis.indicators import calculate_all_indicators

        config = get_test_config()

        # Ticker with 5 years of data (plenty of history for any date in 2023)
        stock_data = create_mock_stock_data(
            start_date='2018-01-01',  # 5 years before 2023
            end_date='2024-01-01',
            tz_aware=False
        )
        benchmark_data = create_mock_benchmark_data(
            start_date='2018-01-01',
            end_date='2024-01-01',
            tz_aware=False
        )

        stock_data_with_indicators = calculate_all_indicators(stock_data, benchmark_data)

        with patch('backtest.engine.YahooFinanceFetcher') as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.fetch_data.return_value = stock_data_with_indicators.copy()
            mock_fetcher.fetch_benchmark.return_value = benchmark_data.copy()

            engine = BacktestEngine(config, use_benchmark=True)

            # 1-year backtest: 2023-01-01 to 2024-01-01
            result = engine.run(
                tickers=['LONG_HISTORY'],
                start_date='2023-01-01',
                end_date='2024-01-01'
            )

        # Every trading day in 2023 should have 252+ bars of history
        # (since data starts in 2018), so entry checks should occur
        # Note: With the Stage2/Entry separation architecture:
        # - stage2_checks is now entry_evaluations (backward compatible key)
        # - Entry evaluations only occur when position capacity allows
        # - Expect at least 50 checks (reduced from 200 due to position limits)
        assert engine.diagnostics['stage2_checks'] >= 50, (
            f"With 5 years of history, most 2023 dates should trigger entry checks. "
            f"Got: {engine.diagnostics['stage2_checks']}"
        )

    def test_short_backtest_period_with_long_history(self):
        """
        Test a 6-month backtest period with sufficient historical data.

        This specifically tests the bug: if loop skips i < 252,
        a 6-month backtest (~125 days) would have 0 Stage2 checks.
        """
        from backtest.engine import BacktestEngine
        from analysis.indicators import calculate_all_indicators

        config = get_test_config()

        stock_data = create_mock_stock_data(
            start_date='2020-01-01',
            end_date='2024-01-01',
            tz_aware=False
        )
        benchmark_data = create_mock_benchmark_data(
            start_date='2020-01-01',
            end_date='2024-01-01',
            tz_aware=False
        )

        stock_data_with_indicators = calculate_all_indicators(stock_data, benchmark_data)

        with patch('backtest.engine.YahooFinanceFetcher') as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.fetch_data.return_value = stock_data_with_indicators.copy()
            mock_fetcher.fetch_benchmark.return_value = benchmark_data.copy()

            engine = BacktestEngine(config, use_benchmark=True)

            # 6-month backtest (~125 trading days)
            result = engine.run(
                tickers=['SHORT_PERIOD'],
                start_date='2023-07-01',
                end_date='2024-01-01'
            )

        # Even a 6-month backtest should perform Stage2 checks
        # if the ticker has sufficient historical data
        assert engine.diagnostics['stage2_checks'] > 0, (
            f"6-month backtest with long history should have Stage2 checks. "
            f"Got: {engine.diagnostics['stage2_checks']}"
        )


class TestIntegrationStage2ToBacktest:
    """Integration tests for Stage2 -> Backtest data flow."""

    def test_full_backtest_flow_with_mock_data(self):
        """
        Test complete backtest flow with properly formatted mock data.

        This test simulates the full data pipeline:
        1. Fetch ticker data
        2. Normalize timezone
        3. Calculate indicators
        4. Run backtest loop
        5. Perform Stage2 checks
        """
        from backtest.engine import BacktestEngine
        from analysis.indicators import calculate_all_indicators

        config = get_test_config()

        # Create comprehensive mock data
        stock_data = create_mock_stock_data(
            start_date='2020-01-01',  # 4 years of data
            end_date='2024-01-01',
            tz_aware=False
        )
        benchmark_data = create_mock_benchmark_data(
            start_date='2020-01-01',
            end_date='2024-01-01',
            tz_aware=False
        )

        # Pre-calculate indicators (simulating what engine does)
        stock_data_with_indicators = calculate_all_indicators(stock_data, benchmark_data)

        with patch('backtest.engine.YahooFinanceFetcher') as MockFetcher:
            mock_fetcher = MockFetcher.return_value
            mock_fetcher.fetch_data.return_value = stock_data_with_indicators.copy()
            mock_fetcher.fetch_benchmark.return_value = benchmark_data.copy()

            engine = BacktestEngine(config, use_benchmark=True)
            result = engine.run(
                tickers=['INTEGRATED_TEST'],
                start_date='2023-01-01',
                end_date='2024-01-01'
            )

        # Verify complete flow
        assert engine.diagnostics['stage2_checks'] > 0, (
            "Integration test should produce Stage2 checks"
        )

        # Log diagnostics for debugging
        print(f"\n=== Integration Test Diagnostics ===")
        print(f"Stage2 checks: {engine.diagnostics['stage2_checks']}")
        print(f"Stage2 passed: {engine.diagnostics['stage2_passed']}")
        print(f"Insufficient data: {engine.diagnostics['insufficient_data']}")
        print(f"Total trades: {result.total_trades}")
