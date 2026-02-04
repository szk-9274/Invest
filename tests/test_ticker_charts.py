"""
Tests for Ticker Charts - Candlestick Chart Visualization

TDD Test Suite for Task 4: Verify that ticker charts correctly:
- Generate candlestick charts with SMA20/SMA50 overlays
- Mark ENTRY positions with up arrows
- Mark EXIT positions with down arrows
- Generate charts for top/bottom performers
- Save charts to output/charts/{TICKER}.png
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


class TestTickerCharts:
    """Tests for TickerCharts class."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_stock_data(self):
        """Create sample stock data with sufficient history."""
        days = 365
        np.random.seed(42)
        dates = pd.date_range(end=datetime(2024, 12, 31), periods=days, freq='D')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'high': prices * (1 + np.random.uniform(0, 0.02, days)),
            'low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    @pytest.fixture
    def sample_trades(self):
        """Sample trades for chart markers."""
        return [
            {'date': datetime(2024, 3, 15), 'ticker': 'AAPL', 'action': 'ENTRY', 'price': 105.0},
            {'date': datetime(2024, 5, 20), 'ticker': 'AAPL', 'action': 'EXIT', 'price': 115.0},
            {'date': datetime(2024, 7, 10), 'ticker': 'AAPL', 'action': 'ENTRY', 'price': 112.0},
            {'date': datetime(2024, 9, 25), 'ticker': 'AAPL', 'action': 'EXIT', 'price': 120.0},
        ]

    def test_ticker_charts_initialization(self, temp_output_dir):
        """Test that TickerCharts initializes correctly."""
        from backtest.ticker_charts import TickerCharts

        charts = TickerCharts(output_dir=temp_output_dir)
        assert charts is not None
        assert charts.output_dir == temp_output_dir

    def test_create_chart_creates_png_file(self, temp_output_dir, sample_stock_data, sample_trades):
        """Test that create_chart generates a PNG file."""
        from backtest.ticker_charts import TickerCharts

        charts = TickerCharts(output_dir=temp_output_dir)
        chart_path = charts.create_chart(
            ticker='AAPL',
            data=sample_stock_data,
            trades=sample_trades
        )

        assert chart_path is not None
        assert os.path.exists(chart_path)
        assert chart_path.endswith('AAPL.png')

    def test_chart_saved_in_charts_subdirectory(self, temp_output_dir, sample_stock_data, sample_trades):
        """Test that charts are saved in charts/ subdirectory."""
        from backtest.ticker_charts import TickerCharts

        charts = TickerCharts(output_dir=temp_output_dir)
        chart_path = charts.create_chart(
            ticker='AAPL',
            data=sample_stock_data,
            trades=sample_trades
        )

        # Chart should be in output_dir/charts/
        expected_dir = os.path.join(temp_output_dir, 'charts')
        assert os.path.dirname(chart_path) == expected_dir

    def test_create_chart_with_no_trades(self, temp_output_dir, sample_stock_data):
        """Test creating chart with no trades (no markers)."""
        from backtest.ticker_charts import TickerCharts

        charts = TickerCharts(output_dir=temp_output_dir)
        chart_path = charts.create_chart(
            ticker='AAPL',
            data=sample_stock_data,
            trades=[]
        )

        assert os.path.exists(chart_path)

    def test_create_charts_for_tickers(self, temp_output_dir, sample_stock_data, sample_trades):
        """Test creating charts for multiple tickers."""
        from backtest.ticker_charts import TickerCharts

        # Create data for multiple tickers
        ticker_data = {
            'AAPL': sample_stock_data.copy(),
            'GOOGL': sample_stock_data.copy(),
            'MSFT': sample_stock_data.copy()
        }

        trades_by_ticker = {
            'AAPL': sample_trades,
            'GOOGL': [{'date': datetime(2024, 4, 1), 'ticker': 'GOOGL', 'action': 'ENTRY', 'price': 100.0}],
            'MSFT': []
        }

        charts = TickerCharts(output_dir=temp_output_dir)
        chart_paths = charts.create_charts_for_tickers(
            tickers=['AAPL', 'GOOGL', 'MSFT'],
            ticker_data=ticker_data,
            trades_by_ticker=trades_by_ticker
        )

        assert len(chart_paths) == 3
        for ticker, path in chart_paths.items():
            assert os.path.exists(path)
            assert ticker in path

    def test_handles_missing_ticker_data(self, temp_output_dir, sample_stock_data):
        """Test handling when ticker data is not available."""
        from backtest.ticker_charts import TickerCharts

        ticker_data = {'AAPL': sample_stock_data}  # Only AAPL has data

        charts = TickerCharts(output_dir=temp_output_dir)
        chart_paths = charts.create_charts_for_tickers(
            tickers=['AAPL', 'MISSING'],  # MISSING has no data
            ticker_data=ticker_data,
            trades_by_ticker={}
        )

        # Only AAPL should have a chart
        assert 'AAPL' in chart_paths
        assert 'MISSING' not in chart_paths

    def test_extract_trades_for_ticker(self, temp_output_dir):
        """Test extracting trades for a specific ticker from trade log."""
        from backtest.ticker_charts import TickerCharts

        all_trades = [
            {'date': datetime(2024, 3, 1), 'ticker': 'AAPL', 'action': 'ENTRY', 'price': 170.0},
            {'date': datetime(2024, 3, 15), 'ticker': 'AAPL', 'action': 'EXIT', 'price': 180.0},
            {'date': datetime(2024, 3, 10), 'ticker': 'GOOGL', 'action': 'ENTRY', 'price': 140.0},
            {'date': datetime(2024, 3, 25), 'ticker': 'GOOGL', 'action': 'EXIT', 'price': 137.0},
        ]

        charts = TickerCharts(output_dir=temp_output_dir)
        aapl_trades = charts.extract_trades_for_ticker('AAPL', all_trades)

        assert len(aapl_trades) == 2
        assert all(t['ticker'] == 'AAPL' for t in aapl_trades)

    def test_get_marker_dates(self, temp_output_dir):
        """Test extracting entry and exit marker dates."""
        from backtest.ticker_charts import TickerCharts

        trades = [
            {'date': datetime(2024, 3, 15), 'ticker': 'AAPL', 'action': 'ENTRY', 'price': 105.0},
            {'date': datetime(2024, 5, 20), 'ticker': 'AAPL', 'action': 'EXIT', 'price': 115.0},
            {'date': datetime(2024, 7, 10), 'ticker': 'AAPL', 'action': 'ENTRY', 'price': 112.0},
        ]

        charts = TickerCharts(output_dir=temp_output_dir)
        entry_dates, exit_dates = charts.get_marker_dates(trades)

        assert len(entry_dates) == 2
        assert len(exit_dates) == 1
        assert datetime(2024, 3, 15) in entry_dates
        assert datetime(2024, 5, 20) in exit_dates


class TestTickerChartsWithMplfinance:
    """Tests that verify mplfinance integration."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_stock_data(self):
        """Create sample OHLCV data."""
        days = 365
        np.random.seed(42)
        dates = pd.date_range(end=datetime(2024, 12, 31), periods=days, freq='D')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'high': prices * (1 + np.random.uniform(0, 0.02, days)),
            'low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    def test_mplfinance_available(self):
        """Test that mplfinance is importable."""
        try:
            import mplfinance
            assert True
        except ImportError:
            pytest.skip("mplfinance not installed - skipping chart tests")

    def test_chart_contains_sma_overlays(self, temp_output_dir, sample_stock_data):
        """Test that chart includes SMA20 and SMA50 overlays."""
        try:
            import mplfinance
        except ImportError:
            pytest.skip("mplfinance not installed")

        from backtest.ticker_charts import TickerCharts

        charts = TickerCharts(output_dir=temp_output_dir)

        # Verify SMAs are calculated
        assert charts.sma_periods == [20, 50]

        # Create chart and verify no error
        chart_path = charts.create_chart(
            ticker='AAPL',
            data=sample_stock_data,
            trades=[]
        )
        assert os.path.exists(chart_path)


class TestTickerChartsGracefulDegradation:
    """Tests for graceful failure when mplfinance is not available."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_handles_missing_mplfinance(self, temp_output_dir):
        """Test graceful handling when mplfinance is not installed."""
        from backtest.ticker_charts import TickerCharts

        charts = TickerCharts(output_dir=temp_output_dir)

        # Should not raise even if mplfinance unavailable
        # (chart generation should be skipped with a warning)
        assert charts is not None
