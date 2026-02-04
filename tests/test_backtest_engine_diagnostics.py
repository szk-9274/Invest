"""
Tests for BacktestEngine diagnostics - Universe Size Display Bug Fix

TDD Test Suite for Task 1: Verify that the engine correctly tracks and displays:
- Stage2 input ticker count (before data fetch)
- Actual universe after data fetch
- Number of filtered-out tickers
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from backtest.engine import BacktestEngine


class TestUniverseSizeDiagnostics:
    """Tests for universe size tracking in BacktestEngine."""

    @pytest.fixture
    def mock_config(self):
        """Minimal config for testing."""
        return {
            'stage': {
                'sma_periods': [50, 150, 200],
                'min_price_above_52w_low': 1.30,
                'max_distance_from_52w_high': 0.75,
                'min_slope_200_days': 20,
                'rs_min_rating': 70,
                'rs_new_high_required': True,
                'min_volume': 500000,
                'auto_fallback_enabled': False,
                'min_trades_threshold': 1
            },
            'vcp': {
                'base_period_min': 35,
                'base_period_max': 65,
                'contraction_sequence': [0.25, 0.15, 0.08, 0.05],
                'last_contraction_max': 0.10,
                'dryup_vol_ratio': 0.6,
                'breakout_vol_ratio': 1.5,
                'pivot_min_high_52w_ratio': 0.95,
                'pivot_buffer_atr': 0.5
            },
            'backtest': {
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'initial_capital': 100000,
                'max_positions': 5,
                'commission': 0.001
            },
            'risk': {
                'risk_per_trade': 0.0075
            },
            'performance': {
                'request_delay': 0.0
            }
        }

    @pytest.fixture
    def create_stock_data(self):
        """Factory to create stock data with specified number of days."""
        def _create(days=300, start_price=100):
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            np.random.seed(42)
            returns = np.random.normal(0.0005, 0.02, days)
            prices = start_price * np.exp(np.cumsum(returns))

            df = pd.DataFrame({
                'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
                'high': prices * (1 + np.random.uniform(0, 0.02, days)),
                'low': prices * (1 - np.random.uniform(0, 0.02, days)),
                'close': prices,
                'volume': np.random.randint(1000000, 10000000, days)
            }, index=dates)
            return df
        return _create

    def test_diagnostics_tracks_stage2_input_count(self, mock_config):
        """
        Test that diagnostics tracks the Stage2 input ticker count
        BEFORE any data fetch filtering.
        """
        engine = BacktestEngine(mock_config, use_benchmark=False)

        # Verify diagnostics key exists and is initialized
        assert 'stage2_universe_size' in engine.diagnostics
        assert engine.diagnostics['stage2_universe_size'] == 0

    def test_diagnostics_records_input_tickers_before_fetch(self, mock_config, create_stock_data):
        """
        Test that when run() is called with N tickers, the diagnostics
        records N as stage2_universe_size BEFORE data fetch filtering.
        """
        engine = BacktestEngine(mock_config, use_benchmark=False)

        input_tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']

        # Mock the fetcher to return None for some tickers (simulating fetch failures)
        def mock_fetch(ticker, period='5y'):
            if ticker in ['AAPL', 'GOOGL', 'MSFT']:
                return create_stock_data(days=300)
            return None  # AMZN and META fail to fetch

        with patch.object(engine.fetcher, 'fetch_data', side_effect=mock_fetch):
            with patch.object(engine.fetcher, 'fetch_benchmark', return_value=None):
                result = engine.run(
                    input_tickers,
                    mock_config['backtest']['start_date'],
                    mock_config['backtest']['end_date']
                )

        # Stage2 input should be 5 (all input tickers)
        assert engine.diagnostics['stage2_universe_size'] == 5

    def test_diagnostics_tracks_filtered_tickers(self, mock_config, create_stock_data):
        """
        Test that diagnostics can determine how many tickers were filtered out
        during data fetch (insufficient data or fetch failures).
        """
        engine = BacktestEngine(mock_config, use_benchmark=False)

        input_tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']

        # Mock: 3 succeed, 2 fail (insufficient data)
        def mock_fetch(ticker, period='5y'):
            if ticker in ['AAPL', 'GOOGL', 'MSFT']:
                return create_stock_data(days=300)
            elif ticker == 'AMZN':
                # Return data with insufficient bars
                return create_stock_data(days=100)
            return None  # META fails completely

        with patch.object(engine.fetcher, 'fetch_data', side_effect=mock_fetch):
            with patch.object(engine.fetcher, 'fetch_benchmark', return_value=None):
                result = engine.run(
                    input_tickers,
                    mock_config['backtest']['start_date'],
                    mock_config['backtest']['end_date']
                )

        # Stage2 input = 5
        # After data fetch = 3 (AAPL, GOOGL, MSFT have 300 bars)
        # Filtered out = 2 (AMZN insufficient data, META fetch failed)
        assert engine.diagnostics['stage2_universe_size'] == 5
        # We need a new diagnostic key to track post-fetch count
        assert 'data_fetch_success_count' in engine.diagnostics
        assert engine.diagnostics['data_fetch_success_count'] == 3
        assert 'data_fetch_filtered_count' in engine.diagnostics
        assert engine.diagnostics['data_fetch_filtered_count'] == 2

    def test_diagnostics_logs_correct_universe_sizes(self, mock_config, create_stock_data, caplog):
        """
        Test that the logging output shows correct universe size information.
        """
        import logging
        caplog.set_level(logging.INFO)

        engine = BacktestEngine(mock_config, use_benchmark=False)

        input_tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']

        def mock_fetch(ticker, period='5y'):
            if ticker in ['AAPL', 'GOOGL', 'MSFT']:
                return create_stock_data(days=300)
            return None

        with patch.object(engine.fetcher, 'fetch_data', side_effect=mock_fetch):
            with patch.object(engine.fetcher, 'fetch_benchmark', return_value=None):
                # Suppress loguru and capture with caplog
                with patch('backtest.engine.logger') as mock_logger:
                    info_calls = []
                    mock_logger.info = lambda msg: info_calls.append(msg)
                    mock_logger.warning = Mock()
                    mock_logger.error = Mock()
                    mock_logger.debug = Mock()

                    result = engine.run(
                        input_tickers,
                        mock_config['backtest']['start_date'],
                        mock_config['backtest']['end_date']
                    )

                    # Check that universe size information was logged
                    log_text = '\n'.join(info_calls)
                    assert 'Stage2 input tickers' in log_text or 'stage2_universe_size' in log_text.lower()

    def test_empty_ticker_list(self, mock_config):
        """
        Test behavior with empty ticker list.
        """
        engine = BacktestEngine(mock_config, use_benchmark=False)

        with patch.object(engine.fetcher, 'fetch_data', return_value=None):
            with patch.object(engine.fetcher, 'fetch_benchmark', return_value=None):
                result = engine.run(
                    [],
                    mock_config['backtest']['start_date'],
                    mock_config['backtest']['end_date']
                )

        assert engine.diagnostics['stage2_universe_size'] == 0
        assert result.total_trades == 0

    def test_all_tickers_filtered_out(self, mock_config, create_stock_data):
        """
        Test when all tickers fail data fetch filtering.
        """
        engine = BacktestEngine(mock_config, use_benchmark=False)

        input_tickers = ['AAPL', 'GOOGL', 'MSFT']

        # All return insufficient data
        def mock_fetch(ticker, period='5y'):
            return create_stock_data(days=100)  # < 252 required

        with patch.object(engine.fetcher, 'fetch_data', side_effect=mock_fetch):
            with patch.object(engine.fetcher, 'fetch_benchmark', return_value=None):
                result = engine.run(
                    input_tickers,
                    mock_config['backtest']['start_date'],
                    mock_config['backtest']['end_date']
                )

        # Input was 3
        assert engine.diagnostics['stage2_universe_size'] == 3
        # After fetch = 0
        assert engine.diagnostics.get('data_fetch_success_count', 0) == 0
        # Filtered = 3
        assert engine.diagnostics.get('data_fetch_filtered_count', 0) == 3
        # No trades possible
        assert result.total_trades == 0
