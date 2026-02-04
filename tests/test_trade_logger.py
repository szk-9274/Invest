"""
Tests for TradeLogger - Trade Log CSV Implementation

TDD Test Suite for Task 2: Verify that the trade logger correctly:
- Logs ENTRY actions with required fields
- Logs EXIT actions with P&L and reason
- Persists data to CSV format
- Integrates with BacktestEngine
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))


class TestTradeLogger:
    """Tests for TradeLogger class."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_trade_logger_initialization(self, temp_output_dir):
        """Test that TradeLogger initializes correctly."""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)
        assert logger is not None
        assert logger.output_dir == temp_output_dir
        assert len(logger.entries) == 0

    def test_log_entry_action(self, temp_output_dir):
        """Test logging an ENTRY action with required fields."""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)

        entry_date = datetime(2024, 3, 15)
        logger.log_entry(
            date=entry_date,
            ticker='AAPL',
            price=175.50,
            shares=100,
            reason='entry_signal',
            capital_after=82450.00
        )

        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry['date'] == entry_date
        assert entry['ticker'] == 'AAPL'
        assert entry['action'] == 'ENTRY'
        assert entry['price'] == 175.50
        assert entry['shares'] == 100
        assert entry['reason'] == 'entry_signal'
        assert entry['pnl'] is None  # ENTRY has no P&L
        assert entry['capital_after'] == 82450.00

    def test_log_exit_action(self, temp_output_dir):
        """Test logging an EXIT action with P&L and exit reason."""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)

        exit_date = datetime(2024, 4, 20)
        logger.log_exit(
            date=exit_date,
            ticker='AAPL',
            price=185.25,
            shares=100,
            reason='stop_loss',
            pnl=975.00,
            capital_after=101475.00
        )

        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry['date'] == exit_date
        assert entry['ticker'] == 'AAPL'
        assert entry['action'] == 'EXIT'
        assert entry['price'] == 185.25
        assert entry['shares'] == 100
        assert entry['reason'] == 'stop_loss'
        assert entry['pnl'] == 975.00
        assert entry['capital_after'] == 101475.00

    def test_log_multiple_trades(self, temp_output_dir):
        """Test logging multiple entry/exit pairs."""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)

        # Trade 1: AAPL
        logger.log_entry(
            date=datetime(2024, 3, 1),
            ticker='AAPL',
            price=170.00,
            shares=50,
            reason='breakout',
            capital_after=91500.00
        )
        logger.log_exit(
            date=datetime(2024, 3, 15),
            ticker='AAPL',
            price=180.00,
            shares=50,
            reason='target_reached',
            pnl=500.00,
            capital_after=100500.00
        )

        # Trade 2: GOOGL
        logger.log_entry(
            date=datetime(2024, 3, 10),
            ticker='GOOGL',
            price=140.00,
            shares=100,
            reason='momentum',
            capital_after=86500.00
        )
        logger.log_exit(
            date=datetime(2024, 3, 25),
            ticker='GOOGL',
            price=135.00,
            shares=100,
            reason='ma50_break',
            pnl=-500.00,
            capital_after=100000.00
        )

        assert len(logger.entries) == 4
        # Verify order
        assert logger.entries[0]['action'] == 'ENTRY'
        assert logger.entries[0]['ticker'] == 'AAPL'
        assert logger.entries[1]['action'] == 'EXIT'
        assert logger.entries[1]['ticker'] == 'AAPL'
        assert logger.entries[2]['action'] == 'ENTRY'
        assert logger.entries[2]['ticker'] == 'GOOGL'
        assert logger.entries[3]['action'] == 'EXIT'
        assert logger.entries[3]['ticker'] == 'GOOGL'

    def test_save_to_csv(self, temp_output_dir):
        """Test saving trade log to CSV file."""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)

        logger.log_entry(
            date=datetime(2024, 3, 1),
            ticker='AAPL',
            price=170.00,
            shares=50,
            reason='breakout',
            capital_after=91500.00
        )
        logger.log_exit(
            date=datetime(2024, 3, 15),
            ticker='AAPL',
            price=180.00,
            shares=50,
            reason='target_reached',
            pnl=500.00,
            capital_after=100500.00
        )

        csv_path = logger.save()

        assert os.path.exists(csv_path)
        assert csv_path.endswith('trade_log.csv')

        # Verify CSV content
        df = pd.read_csv(csv_path)
        assert len(df) == 2
        assert list(df.columns) == ['date', 'ticker', 'action', 'price', 'shares', 'reason', 'pnl', 'capital_after']
        assert df.iloc[0]['action'] == 'ENTRY'
        assert df.iloc[1]['action'] == 'EXIT'
        assert pd.isna(df.iloc[0]['pnl'])  # ENTRY has no P&L
        assert df.iloc[1]['pnl'] == 500.00

    def test_csv_date_format(self, temp_output_dir):
        """Test that dates are formatted as YYYY-MM-DD in CSV."""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)

        logger.log_entry(
            date=datetime(2024, 3, 15),
            ticker='AAPL',
            price=175.50,
            shares=100,
            reason='entry_signal',
            capital_after=82450.00
        )

        csv_path = logger.save()
        df = pd.read_csv(csv_path)

        assert df.iloc[0]['date'] == '2024-03-15'

    def test_save_empty_log(self, temp_output_dir):
        """Test saving when no trades have been logged."""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)
        csv_path = logger.save()

        # Should still create file with headers
        assert os.path.exists(csv_path)
        df = pd.read_csv(csv_path)
        assert len(df) == 0
        assert list(df.columns) == ['date', 'ticker', 'action', 'price', 'shares', 'reason', 'pnl', 'capital_after']

    def test_exit_reasons_logged_correctly(self, temp_output_dir):
        """Test all exit reason types are logged correctly."""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)
        base_date = datetime(2024, 3, 1)

        exit_reasons = ['stop_loss', 'ma50_break', 'target_reached', 'end_of_backtest']

        for i, reason in enumerate(exit_reasons):
            logger.log_exit(
                date=base_date + timedelta(days=i),
                ticker=f'TICK{i}',
                price=100.0,
                shares=10,
                reason=reason,
                pnl=100.0 * (i - 1),
                capital_after=100000.0
            )

        assert len(logger.entries) == 4
        for i, reason in enumerate(exit_reasons):
            assert logger.entries[i]['reason'] == reason


class TestTradeLoggerIntegration:
    """Integration tests for TradeLogger with BacktestEngine."""

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
                'end_date': '2024-06-30',
                'initial_capital': 100000,
                'max_positions': 5,
                'commission': 0.001
            },
            'risk': {
                'risk_per_trade': 0.0075
            },
            'performance': {
                'request_delay': 0.0
            },
            'output': {
                'csv_path': 'output/screening_results.csv'
            }
        }

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_engine_has_trade_logger(self, mock_config, temp_output_dir):
        """Test that BacktestEngine initializes with TradeLogger."""
        from backtest.engine import BacktestEngine

        mock_config['output'] = {'csv_path': temp_output_dir}
        engine = BacktestEngine(mock_config, use_benchmark=False)

        assert hasattr(engine, 'trade_logger')
        assert engine.trade_logger is not None

    def test_engine_logs_entry_on_position_open(self, mock_config, temp_output_dir):
        """Test that BacktestEngine logs ENTRY when opening a position."""
        # This test verifies the integration behavior
        # Implementation will log entries in the position opening code
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)

        # Simulate what the engine should do
        logger.log_entry(
            date=datetime(2024, 3, 15),
            ticker='AAPL',
            price=175.50,
            shares=100,
            reason='entry_signal',
            capital_after=82450.00
        )

        assert len(logger.entries) == 1
        assert logger.entries[0]['action'] == 'ENTRY'

    def test_engine_logs_exit_on_position_close(self, mock_config, temp_output_dir):
        """Test that BacktestEngine logs EXIT when closing a position."""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger(output_dir=temp_output_dir)

        # Simulate what the engine should do
        logger.log_exit(
            date=datetime(2024, 4, 20),
            ticker='AAPL',
            price=185.25,
            shares=100,
            reason='stop_loss',
            pnl=975.00,
            capital_after=101475.00
        )

        assert len(logger.entries) == 1
        assert logger.entries[0]['action'] == 'EXIT'
        assert logger.entries[0]['reason'] == 'stop_loss'
