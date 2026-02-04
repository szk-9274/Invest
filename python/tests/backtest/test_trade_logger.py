"""
Tests for TradeLogger class - Compatibility Layer

This file validates that TradeLogger works with the current API.
Comprehensive tests are in tests/test_trade_logger.py
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestTradeLoggerCompat:
    """Compatibility tests for TradeLogger"""

    def test_trade_logger_exists(self):
        """TradeLogger class should exist"""
        from backtest.trade_logger import TradeLogger
        assert TradeLogger is not None

    def test_trade_logger_initialization(self):
        """TradeLogger should accept output_dir parameter"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TradeLogger(output_dir=tmpdir)
            assert logger is not None
            assert logger.output_dir == tmpdir
            assert len(logger.entries) == 0

    def test_log_entry(self):
        """log_entry should work with current API"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TradeLogger(output_dir=tmpdir)
            logger.log_entry(
                date=datetime(2024, 1, 15),
                ticker='AAPL',
                price=150.0,
                shares=100,
                reason='breakout',
                capital_after=91500.0
            )
            assert len(logger.entries) == 1
            assert logger.entries[0]['action'] == 'ENTRY'
            assert logger.entries[0]['ticker'] == 'AAPL'

    def test_log_exit(self):
        """log_exit should work with current API"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TradeLogger(output_dir=tmpdir)
            logger.log_exit(
                date=datetime(2024, 2, 1),
                ticker='AAPL',
                price=160.0,
                shares=100,
                reason='target_reached',
                pnl=1000.0,
                capital_after=101000.0
            )
            assert len(logger.entries) == 1
            assert logger.entries[0]['action'] == 'EXIT'
            assert logger.entries[0]['pnl'] == 1000.0

    def test_save(self):
        """save should create CSV file"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TradeLogger(output_dir=tmpdir)
            logger.log_entry(
                date=datetime(2024, 1, 15),
                ticker='AAPL',
                price=150.0,
                shares=100,
                reason='breakout',
                capital_after=91500.0
            )
            saved_path = logger.save()
            assert Path(saved_path).exists()
            assert 'trade_log.csv' in saved_path

    def test_get_entries_df(self):
        """get_entries_df should return DataFrame"""
        from backtest.trade_logger import TradeLogger
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TradeLogger(output_dir=tmpdir)
            logger.log_entry(
                date=datetime(2024, 1, 15),
                ticker='AAPL',
                price=150.0,
                shares=100,
                reason='breakout',
                capital_after=91500.0
            )
            df = logger.get_entries_df()
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1

    def test_get_exit_entries(self):
        """get_exit_entries should return only EXIT entries"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TradeLogger(output_dir=tmpdir)
            logger.log_entry(
                date=datetime(2024, 1, 15),
                ticker='AAPL',
                price=150.0,
                shares=100,
                reason='breakout',
                capital_after=91500.0
            )
            logger.log_exit(
                date=datetime(2024, 2, 1),
                ticker='AAPL',
                price=160.0,
                shares=100,
                reason='target_reached',
                pnl=1000.0,
                capital_after=101000.0
            )
            exits = logger.get_exit_entries()
            assert len(exits) == 1
            assert exits[0]['action'] == 'EXIT'

    def test_clear(self):
        """clear should empty entries list"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TradeLogger(output_dir=tmpdir)
            logger.log_entry(
                date=datetime(2024, 1, 15),
                ticker='AAPL',
                price=150.0,
                shares=100,
                reason='breakout',
                capital_after=91500.0
            )
            assert len(logger.entries) == 1
            logger.clear()
            assert len(logger.entries) == 0
