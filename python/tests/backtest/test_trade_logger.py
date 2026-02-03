"""
Tests for TradeLogger class

TDD: Write tests first, then implement.
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
import pandas as pd
import tempfile
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestTradeLoggerInit:
    """Test TradeLogger initialization"""

    def test_trade_logger_exists(self):
        """TradeLogger class should exist"""
        from backtest.trade_logger import TradeLogger
        assert TradeLogger is not None

    def test_trade_logger_initializes_with_output_path(self):
        """TradeLogger should accept output path"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "trades.csv"
            logger = TradeLogger(output_path=output_path)
            assert logger.output_path == output_path

    def test_trade_logger_default_output_path(self):
        """TradeLogger should have default output path"""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger()
        assert logger.output_path is not None
        assert 'trade_log' in str(logger.output_path)


class TestTradeLoggerLogEntry:
    """Test TradeLogger.log_entry() method"""

    def test_log_entry_creates_entry_row(self):
        """log_entry should create ENTRY row in log"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "trades.csv"
            logger = TradeLogger(output_path=output_path)

            logger.log_entry(
                ticker='AAPL',
                entry_date=datetime(2024, 1, 15),
                entry_price=150.0,
                shares=100,
                stop_price=145.0,
                target_price=165.0,
                trade_id=1
            )

            assert len(logger.entries) == 1
            entry = logger.entries[0]
            assert entry['type'] == 'ENTRY'
            assert entry['ticker'] == 'AAPL'
            assert entry['price'] == 150.0
            assert entry['shares'] == 100

    def test_log_entry_includes_required_fields(self):
        """Entry row should have all required fields"""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger()

        logger.log_entry(
            ticker='MSFT',
            entry_date=datetime(2024, 2, 1),
            entry_price=400.0,
            shares=50,
            stop_price=390.0,
            target_price=440.0,
            trade_id=2
        )

        entry = logger.entries[0]
        required_fields = ['type', 'trade_id', 'ticker', 'date', 'price',
                          'shares', 'stop_price', 'target_price']
        for field in required_fields:
            assert field in entry, f"Missing field: {field}"


class TestTradeLoggerLogExit:
    """Test TradeLogger.log_exit() method"""

    def test_log_exit_creates_exit_row(self):
        """log_exit should create EXIT row in log"""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger()

        logger.log_exit(
            ticker='AAPL',
            exit_date=datetime(2024, 2, 20),
            exit_price=160.0,
            shares=100,
            entry_price=150.0,
            exit_reason='target_reached',
            trade_id=1
        )

        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry['type'] == 'EXIT'
        assert entry['ticker'] == 'AAPL'
        assert entry['price'] == 160.0
        assert entry['exit_reason'] == 'target_reached'

    def test_log_exit_calculates_pnl(self):
        """Exit row should include P&L calculation"""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger()

        logger.log_exit(
            ticker='AAPL',
            exit_date=datetime(2024, 2, 20),
            exit_price=160.0,
            shares=100,
            entry_price=150.0,
            exit_reason='target_reached',
            trade_id=1
        )

        entry = logger.entries[0]
        assert 'pnl' in entry
        assert entry['pnl'] == 1000.0  # (160-150) * 100
        assert 'pnl_pct' in entry
        assert abs(entry['pnl_pct'] - 0.0667) < 0.01  # ~6.67%

    def test_log_exit_with_loss(self):
        """Exit with loss should have negative P&L"""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger()

        logger.log_exit(
            ticker='AAPL',
            exit_date=datetime(2024, 2, 20),
            exit_price=140.0,
            shares=100,
            entry_price=150.0,
            exit_reason='stop_loss',
            trade_id=1
        )

        entry = logger.entries[0]
        assert entry['pnl'] == -1000.0  # (140-150) * 100
        assert entry['pnl_pct'] < 0


class TestTradeLoggerSave:
    """Test TradeLogger.save() method"""

    def test_save_creates_csv_file(self):
        """save() should create CSV file"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "trades.csv"
            logger = TradeLogger(output_path=output_path)

            logger.log_entry(
                ticker='AAPL',
                entry_date=datetime(2024, 1, 15),
                entry_price=150.0,
                shares=100,
                stop_price=145.0,
                target_price=165.0,
                trade_id=1
            )

            logger.save()

            assert output_path.exists()

    def test_save_csv_has_correct_columns(self):
        """CSV should have correct column headers"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "trades.csv"
            logger = TradeLogger(output_path=output_path)

            logger.log_entry(
                ticker='AAPL',
                entry_date=datetime(2024, 1, 15),
                entry_price=150.0,
                shares=100,
                stop_price=145.0,
                target_price=165.0,
                trade_id=1
            )

            logger.save()

            df = pd.read_csv(output_path)
            expected_columns = ['type', 'trade_id', 'ticker', 'date', 'price', 'shares']
            for col in expected_columns:
                assert col in df.columns, f"Missing column: {col}"

    def test_save_preserves_chronological_order(self):
        """CSV should preserve chronological order of trades"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "trades.csv"
            logger = TradeLogger(output_path=output_path)

            logger.log_entry(
                ticker='AAPL',
                entry_date=datetime(2024, 1, 15),
                entry_price=150.0,
                shares=100,
                stop_price=145.0,
                target_price=165.0,
                trade_id=1
            )
            logger.log_entry(
                ticker='MSFT',
                entry_date=datetime(2024, 1, 20),
                entry_price=400.0,
                shares=50,
                stop_price=390.0,
                target_price=440.0,
                trade_id=2
            )
            logger.log_exit(
                ticker='AAPL',
                exit_date=datetime(2024, 2, 1),
                exit_price=160.0,
                shares=100,
                entry_price=150.0,
                exit_reason='target_reached',
                trade_id=1
            )

            logger.save()

            df = pd.read_csv(output_path)
            assert len(df) == 3
            # Order should be: AAPL ENTRY, MSFT ENTRY, AAPL EXIT
            assert df.iloc[0]['ticker'] == 'AAPL'
            assert df.iloc[0]['type'] == 'ENTRY'
            assert df.iloc[1]['ticker'] == 'MSFT'
            assert df.iloc[2]['type'] == 'EXIT'


class TestTradeLoggerIntegration:
    """Integration tests for TradeLogger with Position"""

    def test_log_position_entry(self):
        """log_position_entry should log from Position object"""
        from backtest.trade_logger import TradeLogger
        from backtest.engine import Position

        logger = TradeLogger()

        pos = Position(
            ticker='NVDA',
            entry_date=datetime(2024, 3, 1),
            entry_price=800.0,
            shares=10,
            stop_price=780.0,
            target_price=880.0,
            pivot=795.0
        )

        logger.log_position_entry(pos, trade_id=5)

        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry['ticker'] == 'NVDA'
        assert entry['price'] == 800.0

    def test_log_position_exit(self):
        """log_position_exit should log from completed Position"""
        from backtest.trade_logger import TradeLogger
        from backtest.engine import Position

        logger = TradeLogger()

        pos = Position(
            ticker='NVDA',
            entry_date=datetime(2024, 3, 1),
            entry_price=800.0,
            shares=10,
            stop_price=780.0,
            target_price=880.0,
            pivot=795.0,
            exit_date=datetime(2024, 3, 15),
            exit_price=850.0,
            exit_reason='target_reached',
            pnl=500.0,
            pnl_pct=0.0625
        )

        logger.log_position_exit(pos, trade_id=5)

        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry['type'] == 'EXIT'
        assert entry['pnl'] == 500.0


class TestTradeLoggerEdgeCases:
    """Test edge cases for TradeLogger"""

    def test_save_empty_log(self):
        """save() with no entries should create empty file with headers"""
        from backtest.trade_logger import TradeLogger

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "trades.csv"
            logger = TradeLogger(output_path=output_path)

            logger.save()

            assert output_path.exists()
            df = pd.read_csv(output_path)
            assert len(df) == 0
            assert len(df.columns) > 0

    def test_multiple_trades_same_ticker(self):
        """Should handle multiple trades of same ticker"""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger()

        # First trade
        logger.log_entry(
            ticker='AAPL', entry_date=datetime(2024, 1, 1),
            entry_price=150.0, shares=100, stop_price=145.0,
            target_price=165.0, trade_id=1
        )
        logger.log_exit(
            ticker='AAPL', exit_date=datetime(2024, 1, 15),
            exit_price=160.0, shares=100, entry_price=150.0,
            exit_reason='target_reached', trade_id=1
        )

        # Second trade same ticker
        logger.log_entry(
            ticker='AAPL', entry_date=datetime(2024, 2, 1),
            entry_price=155.0, shares=100, stop_price=150.0,
            target_price=170.0, trade_id=2
        )

        assert len(logger.entries) == 3
        aapl_entries = [e for e in logger.entries if e['ticker'] == 'AAPL']
        assert len(aapl_entries) == 3

    def test_get_trade_count(self):
        """get_trade_count should return correct count"""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger()

        logger.log_entry(
            ticker='AAPL', entry_date=datetime(2024, 1, 1),
            entry_price=150.0, shares=100, stop_price=145.0,
            target_price=165.0, trade_id=1
        )
        logger.log_entry(
            ticker='MSFT', entry_date=datetime(2024, 1, 2),
            entry_price=400.0, shares=50, stop_price=390.0,
            target_price=440.0, trade_id=2
        )

        # Should count unique trade_ids of type ENTRY
        assert logger.get_entry_count() == 2

    def test_to_dataframe(self):
        """to_dataframe should return pandas DataFrame"""
        from backtest.trade_logger import TradeLogger

        logger = TradeLogger()

        logger.log_entry(
            ticker='AAPL', entry_date=datetime(2024, 1, 1),
            entry_price=150.0, shares=100, stop_price=145.0,
            target_price=165.0, trade_id=1
        )

        df = logger.to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
