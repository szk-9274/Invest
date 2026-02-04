"""
Tests for Ticker Analysis - Ticker-Level P&L Analysis

TDD Test Suite for Task 3: Verify that ticker analysis correctly:
- Aggregates EXIT trades by ticker
- Calculates total P&L per ticker
- Counts trades per ticker
- Identifies top 5 winners and bottom 5 losers
- Outputs ticker_stats.csv
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


class TestTickerAnalysis:
    """Tests for TickerAnalysis class."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_trade_log_entries(self):
        """Sample trade log entries for testing."""
        return [
            # AAPL: 2 trades, total P&L = +1000
            {'date': datetime(2024, 3, 1), 'ticker': 'AAPL', 'action': 'ENTRY', 'price': 170.0, 'shares': 50, 'reason': 'breakout', 'pnl': None, 'capital_after': 91500.0},
            {'date': datetime(2024, 3, 15), 'ticker': 'AAPL', 'action': 'EXIT', 'price': 180.0, 'shares': 50, 'reason': 'target_reached', 'pnl': 500.0, 'capital_after': 100500.0},
            {'date': datetime(2024, 4, 1), 'ticker': 'AAPL', 'action': 'ENTRY', 'price': 175.0, 'shares': 50, 'reason': 'breakout', 'pnl': None, 'capital_after': 91750.0},
            {'date': datetime(2024, 4, 20), 'ticker': 'AAPL', 'action': 'EXIT', 'price': 185.0, 'shares': 50, 'reason': 'target_reached', 'pnl': 500.0, 'capital_after': 101000.0},

            # GOOGL: 1 trade, total P&L = -300
            {'date': datetime(2024, 3, 10), 'ticker': 'GOOGL', 'action': 'ENTRY', 'price': 140.0, 'shares': 100, 'reason': 'momentum', 'pnl': None, 'capital_after': 86000.0},
            {'date': datetime(2024, 3, 25), 'ticker': 'GOOGL', 'action': 'EXIT', 'price': 137.0, 'shares': 100, 'reason': 'stop_loss', 'pnl': -300.0, 'capital_after': 99700.0},

            # MSFT: 1 trade, total P&L = +800
            {'date': datetime(2024, 4, 5), 'ticker': 'MSFT', 'action': 'ENTRY', 'price': 400.0, 'shares': 20, 'reason': 'breakout', 'pnl': None, 'capital_after': 92000.0},
            {'date': datetime(2024, 4, 30), 'ticker': 'MSFT', 'action': 'EXIT', 'price': 440.0, 'shares': 20, 'reason': 'target_reached', 'pnl': 800.0, 'capital_after': 100800.0},

            # AMZN: 1 trade, total P&L = -500
            {'date': datetime(2024, 5, 1), 'ticker': 'AMZN', 'action': 'ENTRY', 'price': 180.0, 'shares': 50, 'reason': 'momentum', 'pnl': None, 'capital_after': 91000.0},
            {'date': datetime(2024, 5, 15), 'ticker': 'AMZN', 'action': 'EXIT', 'price': 170.0, 'shares': 50, 'reason': 'ma50_break', 'pnl': -500.0, 'capital_after': 99500.0},

            # META: 1 trade, total P&L = +600
            {'date': datetime(2024, 5, 20), 'ticker': 'META', 'action': 'ENTRY', 'price': 500.0, 'shares': 10, 'reason': 'breakout', 'pnl': None, 'capital_after': 95000.0},
            {'date': datetime(2024, 6, 10), 'ticker': 'META', 'action': 'EXIT', 'price': 560.0, 'shares': 10, 'reason': 'end_of_backtest', 'pnl': 600.0, 'capital_after': 100600.0},

            # NVDA: 1 trade, total P&L = +1500
            {'date': datetime(2024, 6, 1), 'ticker': 'NVDA', 'action': 'ENTRY', 'price': 800.0, 'shares': 10, 'reason': 'momentum', 'pnl': None, 'capital_after': 92000.0},
            {'date': datetime(2024, 6, 20), 'ticker': 'NVDA', 'action': 'EXIT', 'price': 950.0, 'shares': 10, 'reason': 'target_reached', 'pnl': 1500.0, 'capital_after': 101500.0},

            # TSLA: 1 trade, total P&L = -700
            {'date': datetime(2024, 6, 5), 'ticker': 'TSLA', 'action': 'ENTRY', 'price': 200.0, 'shares': 50, 'reason': 'breakout', 'pnl': None, 'capital_after': 90000.0},
            {'date': datetime(2024, 6, 25), 'ticker': 'TSLA', 'action': 'EXIT', 'price': 186.0, 'shares': 50, 'reason': 'stop_loss', 'pnl': -700.0, 'capital_after': 99300.0},
        ]

    def test_ticker_analysis_initialization(self, temp_output_dir):
        """Test that TickerAnalysis initializes correctly."""
        from backtest.ticker_analysis import TickerAnalysis

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        assert analyzer is not None
        assert analyzer.output_dir == temp_output_dir

    def test_analyze_from_trade_log_entries(self, temp_output_dir, sample_trade_log_entries):
        """Test analysis from trade log entries."""
        from backtest.ticker_analysis import TickerAnalysis

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        stats = analyzer.analyze(sample_trade_log_entries)

        assert stats is not None
        assert isinstance(stats, pd.DataFrame)
        assert len(stats) == 7  # 7 unique tickers

    def test_aggregates_pnl_by_ticker(self, temp_output_dir, sample_trade_log_entries):
        """Test that P&L is correctly aggregated by ticker."""
        from backtest.ticker_analysis import TickerAnalysis

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        stats = analyzer.analyze(sample_trade_log_entries)

        # AAPL: 500 + 500 = 1000
        aapl_stats = stats[stats['ticker'] == 'AAPL'].iloc[0]
        assert aapl_stats['total_pnl'] == 1000.0

        # GOOGL: -300
        googl_stats = stats[stats['ticker'] == 'GOOGL'].iloc[0]
        assert googl_stats['total_pnl'] == -300.0

        # NVDA: 1500
        nvda_stats = stats[stats['ticker'] == 'NVDA'].iloc[0]
        assert nvda_stats['total_pnl'] == 1500.0

    def test_counts_trades_by_ticker(self, temp_output_dir, sample_trade_log_entries):
        """Test that trade counts are correct per ticker."""
        from backtest.ticker_analysis import TickerAnalysis

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        stats = analyzer.analyze(sample_trade_log_entries)

        # AAPL: 2 trades
        aapl_stats = stats[stats['ticker'] == 'AAPL'].iloc[0]
        assert aapl_stats['trade_count'] == 2

        # GOOGL: 1 trade
        googl_stats = stats[stats['ticker'] == 'GOOGL'].iloc[0]
        assert googl_stats['trade_count'] == 1

    def test_get_top_winners(self, temp_output_dir, sample_trade_log_entries):
        """Test getting top 5 winning tickers."""
        from backtest.ticker_analysis import TickerAnalysis

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        analyzer.analyze(sample_trade_log_entries)
        top_winners = analyzer.get_top_winners(n=5)

        assert len(top_winners) == 5
        # Order should be: NVDA (1500), AAPL (1000), MSFT (800), META (600), and next best
        assert top_winners.iloc[0]['ticker'] == 'NVDA'
        assert top_winners.iloc[0]['total_pnl'] == 1500.0
        assert top_winners.iloc[1]['ticker'] == 'AAPL'
        assert top_winners.iloc[1]['total_pnl'] == 1000.0

    def test_get_bottom_losers(self, temp_output_dir, sample_trade_log_entries):
        """Test getting bottom 5 losing tickers."""
        from backtest.ticker_analysis import TickerAnalysis

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        analyzer.analyze(sample_trade_log_entries)
        bottom_losers = analyzer.get_bottom_losers(n=5)

        assert len(bottom_losers) == 5
        # Order should be: TSLA (-700), AMZN (-500), GOOGL (-300), then winners
        assert bottom_losers.iloc[0]['ticker'] == 'TSLA'
        assert bottom_losers.iloc[0]['total_pnl'] == -700.0
        assert bottom_losers.iloc[1]['ticker'] == 'AMZN'
        assert bottom_losers.iloc[1]['total_pnl'] == -500.0

    def test_save_ticker_stats_csv(self, temp_output_dir, sample_trade_log_entries):
        """Test saving ticker stats to CSV."""
        from backtest.ticker_analysis import TickerAnalysis

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        analyzer.analyze(sample_trade_log_entries)
        csv_path = analyzer.save()

        assert os.path.exists(csv_path)
        assert csv_path.endswith('ticker_stats.csv')

        # Verify CSV content
        df = pd.read_csv(csv_path)
        assert 'ticker' in df.columns
        assert 'total_pnl' in df.columns
        assert 'trade_count' in df.columns
        assert len(df) == 7

    def test_analyze_from_trade_log_csv(self, temp_output_dir):
        """Test loading and analyzing from trade_log.csv file."""
        from backtest.ticker_analysis import TickerAnalysis
        from backtest.trade_logger import TradeLogger

        # Create trade log CSV
        logger = TradeLogger(output_dir=temp_output_dir)
        logger.log_entry(datetime(2024, 3, 1), 'AAPL', 170.0, 50, 'breakout', 91500.0)
        logger.log_exit(datetime(2024, 3, 15), 'AAPL', 180.0, 50, 'target_reached', 500.0, 100500.0)
        logger.log_entry(datetime(2024, 3, 10), 'GOOGL', 140.0, 100, 'momentum', 86000.0)
        logger.log_exit(datetime(2024, 3, 25), 'GOOGL', 137.0, 100, 'stop_loss', -300.0, 99700.0)
        trade_log_path = logger.save()

        # Analyze from CSV
        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        stats = analyzer.analyze_from_csv(trade_log_path)

        assert len(stats) == 2
        aapl_stats = stats[stats['ticker'] == 'AAPL'].iloc[0]
        assert aapl_stats['total_pnl'] == 500.0

    def test_empty_entries_handling(self, temp_output_dir):
        """Test handling of empty entries."""
        from backtest.ticker_analysis import TickerAnalysis

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        stats = analyzer.analyze([])

        assert stats is not None
        assert len(stats) == 0

    def test_only_entry_trades_no_exits(self, temp_output_dir):
        """Test with only ENTRY trades (no EXITs to analyze)."""
        from backtest.ticker_analysis import TickerAnalysis

        entries = [
            {'date': datetime(2024, 3, 1), 'ticker': 'AAPL', 'action': 'ENTRY', 'price': 170.0, 'shares': 50, 'reason': 'breakout', 'pnl': None, 'capital_after': 91500.0},
        ]

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        stats = analyzer.analyze(entries)

        # Only EXIT trades have P&L, so no stats should be generated
        assert len(stats) == 0

    def test_print_summary(self, temp_output_dir, sample_trade_log_entries, capsys):
        """Test printing summary to console."""
        from backtest.ticker_analysis import TickerAnalysis

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        analyzer.analyze(sample_trade_log_entries)
        analyzer.print_summary()

        captured = capsys.readouterr()
        # Should contain top winners and bottom losers
        assert 'NVDA' in captured.out
        assert 'TSLA' in captured.out


class TestTickerAnalysisEdgeCases:
    """Edge case tests for TickerAnalysis."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_fewer_than_5_tickers(self, temp_output_dir):
        """Test when there are fewer than 5 tickers."""
        from backtest.ticker_analysis import TickerAnalysis

        entries = [
            {'date': datetime(2024, 3, 1), 'ticker': 'AAPL', 'action': 'EXIT', 'price': 180.0, 'shares': 50, 'reason': 'target_reached', 'pnl': 500.0, 'capital_after': 100500.0},
            {'date': datetime(2024, 3, 25), 'ticker': 'GOOGL', 'action': 'EXIT', 'price': 137.0, 'shares': 100, 'reason': 'stop_loss', 'pnl': -300.0, 'capital_after': 99700.0},
        ]

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        analyzer.analyze(entries)

        top_winners = analyzer.get_top_winners(n=5)
        bottom_losers = analyzer.get_bottom_losers(n=5)

        # Should return all available tickers (2)
        assert len(top_winners) == 2
        assert len(bottom_losers) == 2

    def test_all_winners(self, temp_output_dir):
        """Test when all trades are winners."""
        from backtest.ticker_analysis import TickerAnalysis

        entries = [
            {'date': datetime(2024, 3, 1), 'ticker': 'AAPL', 'action': 'EXIT', 'price': 180.0, 'shares': 50, 'reason': 'target_reached', 'pnl': 500.0, 'capital_after': 100500.0},
            {'date': datetime(2024, 3, 25), 'ticker': 'GOOGL', 'action': 'EXIT', 'price': 150.0, 'shares': 100, 'reason': 'target_reached', 'pnl': 1000.0, 'capital_after': 101000.0},
        ]

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        analyzer.analyze(entries)

        bottom_losers = analyzer.get_bottom_losers(n=5)
        # Even though all are winners, it returns bottom N by P&L
        assert len(bottom_losers) == 2
        assert bottom_losers.iloc[0]['total_pnl'] == 500.0  # Lowest winner

    def test_all_losers(self, temp_output_dir):
        """Test when all trades are losers."""
        from backtest.ticker_analysis import TickerAnalysis

        entries = [
            {'date': datetime(2024, 3, 1), 'ticker': 'AAPL', 'action': 'EXIT', 'price': 160.0, 'shares': 50, 'reason': 'stop_loss', 'pnl': -500.0, 'capital_after': 99500.0},
            {'date': datetime(2024, 3, 25), 'ticker': 'GOOGL', 'action': 'EXIT', 'price': 130.0, 'shares': 100, 'reason': 'stop_loss', 'pnl': -1000.0, 'capital_after': 99000.0},
        ]

        analyzer = TickerAnalysis(output_dir=temp_output_dir)
        analyzer.analyze(entries)

        top_winners = analyzer.get_top_winners(n=5)
        # Even though all are losers, it returns top N by P&L
        assert len(top_winners) == 2
        assert top_winners.iloc[0]['total_pnl'] == -500.0  # Least negative
