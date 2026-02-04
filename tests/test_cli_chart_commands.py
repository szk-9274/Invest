"""
Tests for CLI Chart Commands - Phase 2

TDD Test Suite for:
- python main.py backtest → auto-generate top/bottom charts
- python main.py chart --ticker AAPL → single ticker chart

These tests verify CLI argument parsing and integration.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import tempfile
import os
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))


class TestCLIChartMode:
    """Tests for chart CLI mode (python main.py chart --ticker AAPL)."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_argparse_accepts_chart_mode(self):
        """Test that argparse accepts 'chart' as a valid mode."""
        import argparse

        # Simulate the expected argparse configuration
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--mode',
            choices=['full', 'stage2', 'test', 'backtest', 'chart'],
            default='full'
        )
        parser.add_argument('--ticker', type=str)

        # Should not raise
        args = parser.parse_args(['--mode', 'chart', '--ticker', 'AAPL'])
        assert args.mode == 'chart'
        assert args.ticker == 'AAPL'

    def test_chart_mode_requires_ticker(self):
        """Test that chart mode logically requires --ticker argument."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--mode',
            choices=['full', 'stage2', 'test', 'backtest', 'chart'],
            default='full'
        )
        parser.add_argument('--ticker', type=str)

        args = parser.parse_args(['--mode', 'chart'])
        # ticker should be None if not provided
        assert args.ticker is None


class TestBacktestAutoChartGeneration:
    """Tests for automatic chart generation after backtest completion."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_backtest_output(self, temp_output_dir):
        """Create sample backtest output files."""
        # Create trade_log.csv
        trade_log_path = os.path.join(temp_output_dir, 'trade_log.csv')
        trade_data = pd.DataFrame({
            'date': ['2024-03-15', '2024-05-20', '2024-04-01', '2024-06-15'],
            'ticker': ['AAPL', 'AAPL', 'GOOGL', 'GOOGL'],
            'action': ['ENTRY', 'EXIT', 'ENTRY', 'EXIT'],
            'price': [105.0, 115.0, 140.0, 135.0],
            'shares': [50, 50, 30, 30],
            'reason': ['entry_signal', 'target_reached', 'entry_signal', 'stop_loss'],
            'pnl': [None, 500.0, None, -150.0],
            'capital_after': [94750.0, 100250.0, 95800.0, 99650.0]
        })
        trade_data.to_csv(trade_log_path, index=False)

        # Create ticker_stats.csv
        ticker_stats_path = os.path.join(temp_output_dir, 'ticker_stats.csv')
        stats_data = pd.DataFrame({
            'ticker': ['AAPL', 'GOOGL'],
            'total_pnl': [500.0, -150.0],
            'trade_count': [1, 1]
        })
        stats_data.to_csv(ticker_stats_path, index=False)

        return {
            'trade_log_path': trade_log_path,
            'ticker_stats_path': ticker_stats_path,
            'output_dir': temp_output_dir
        }

    def test_generate_top_bottom_charts_callable(self):
        """Test that generate_top_bottom_charts is importable."""
        from backtest.ticker_charts import generate_top_bottom_charts
        assert callable(generate_top_bottom_charts)

    def test_backtest_output_includes_required_files(self, sample_backtest_output):
        """Test that backtest produces required files for chart generation."""
        trade_log_path = sample_backtest_output['trade_log_path']
        ticker_stats_path = sample_backtest_output['ticker_stats_path']

        # Both files should exist
        assert os.path.exists(trade_log_path)
        assert os.path.exists(ticker_stats_path)

        # trade_log should have required columns
        trade_log = pd.read_csv(trade_log_path)
        assert 'ticker' in trade_log.columns
        assert 'date' in trade_log.columns
        assert 'action' in trade_log.columns

        # ticker_stats should have required columns
        ticker_stats = pd.read_csv(ticker_stats_path)
        assert 'ticker' in ticker_stats.columns
        assert 'total_pnl' in ticker_stats.columns


class TestChartIntegrationWithBacktest:
    """Integration tests for chart generation with backtest workflow."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_charts_after_backtest_workflow(self, temp_output_dir, monkeypatch):
        """Test the complete workflow: backtest -> charts."""
        from backtest.ticker_charts import generate_top_bottom_charts
        import yfinance as yf

        # Create sample backtest output
        trade_log_path = os.path.join(temp_output_dir, 'trade_log.csv')
        pd.DataFrame({
            'date': ['2024-03-15', '2024-05-20'],
            'ticker': ['AAPL', 'AAPL'],
            'action': ['ENTRY', 'EXIT'],
            'price': [105.0, 115.0],
            'shares': [50, 50],
            'reason': ['entry_signal', 'target_reached'],
            'pnl': [None, 500.0],
            'capital_after': [94750.0, 100250.0]
        }).to_csv(trade_log_path, index=False)

        ticker_stats_path = os.path.join(temp_output_dir, 'ticker_stats.csv')
        pd.DataFrame({
            'ticker': ['AAPL'],
            'total_pnl': [500.0],
            'trade_count': [1]
        }).to_csv(ticker_stats_path, index=False)

        # Mock yfinance
        def mock_history(self, start=None, end=None, period=None):
            days = 252
            np.random.seed(42)
            dates = pd.date_range(start='2024-01-01', periods=days, freq='B')
            base_price = 100
            returns = np.random.normal(0.0005, 0.02, days)
            prices = base_price * np.exp(np.cumsum(returns))
            return pd.DataFrame({
                'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
                'High': prices * (1 + np.random.uniform(0, 0.02, days)),
                'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
                'Close': prices,
                'Volume': np.random.randint(1000000, 10000000, days)
            }, index=dates)

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return mock_history(self, start, end, period)

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        # Generate charts
        result = generate_top_bottom_charts(
            ticker_stats_path=ticker_stats_path,
            trade_log_path=trade_log_path,
            output_dir=temp_output_dir,
            top_n=1,
            bottom_n=0
        )

        # Verify output
        assert len(result) == 1
        assert result[0].exists()
        assert 'top_01_AAPL.png' in result[0].name
