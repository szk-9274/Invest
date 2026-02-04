"""
Tests for TradingView-like Price Chart Generation - Phase 1

TDD Test Suite for generate_price_chart function that creates:
- Dark background (TradingView-like)
- Candlestick chart (daily OHLC)
- Green up candles, red down candles
- SMA 20, 50, 200
- Bollinger Bands (20, 2)
- Volume panel below price
- Clean layout, proper margins, monthly date ticks

Phase 1 ONLY:
- NO trade markers (IN/OUT)
- NO connection to trade_log.csv
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os
from PIL import Image

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))


class TestGeneratePriceChartSignature:
    """Tests for the generate_price_chart function signature and basic behavior."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_year_data(self):
        """Create sample ~1 year of OHLCV data."""
        days = 252  # Trading days in a year
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')  # Business days

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.random.uniform(0, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    def test_function_exists(self):
        """Test that generate_price_chart function exists."""
        from backtest.ticker_charts import generate_price_chart
        assert callable(generate_price_chart)

    def test_function_signature_accepts_required_parameters(self, temp_output_dir):
        """Test that function accepts ticker, start_date, end_date, output_dir."""
        from backtest.ticker_charts import generate_price_chart

        # This should not raise TypeError for missing parameters
        # We expect it might fail for other reasons (no data), but signature is correct
        try:
            result = generate_price_chart(
                ticker="AAPL",
                start_date="2024-01-01",
                end_date="2024-12-31",
                output_dir=temp_output_dir
            )
        except Exception as e:
            # TypeError for missing parameters would indicate signature issue
            assert not isinstance(e, TypeError), f"Signature error: {e}"

    def test_function_accepts_style_parameter(self, temp_output_dir):
        """Test that function accepts optional style parameter."""
        from backtest.ticker_charts import generate_price_chart

        try:
            result = generate_price_chart(
                ticker="AAPL",
                start_date="2024-01-01",
                end_date="2024-12-31",
                output_dir=temp_output_dir,
                style="tradingview"
            )
        except TypeError as e:
            pytest.fail(f"style parameter not accepted: {e}")
        except Exception:
            pass  # Other exceptions are OK for signature test

    def test_returns_path_object(self, temp_output_dir, sample_year_data, monkeypatch):
        """Test that function returns a Path object."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        # Mock yfinance to return our sample data
        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return sample_year_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        result = generate_price_chart(
            ticker="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            output_dir=temp_output_dir
        )

        assert isinstance(result, Path), f"Expected Path, got {type(result)}"


class TestGeneratePriceChartOutput:
    """Tests for output file generation."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_year_data(self):
        """Create sample ~1 year of OHLCV data."""
        days = 252
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.random.uniform(0, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    def test_creates_png_file(self, temp_output_dir, sample_year_data, monkeypatch):
        """Test that function creates a PNG file."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return sample_year_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        result = generate_price_chart(
            ticker="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            output_dir=temp_output_dir
        )

        assert result.exists(), f"File not created: {result}"
        assert result.suffix == '.png', f"Expected .png, got {result.suffix}"

    def test_deterministic_filename(self, temp_output_dir, sample_year_data, monkeypatch):
        """Test that filename follows pattern {ticker}_price_chart.png."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return sample_year_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        result = generate_price_chart(
            ticker="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            output_dir=temp_output_dir
        )

        assert result.name == "AAPL_price_chart.png", f"Expected AAPL_price_chart.png, got {result.name}"

    def test_creates_charts_subdirectory(self, temp_output_dir, sample_year_data, monkeypatch):
        """Test that charts are saved in output_dir/charts/ subdirectory."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return sample_year_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        result = generate_price_chart(
            ticker="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            output_dir=temp_output_dir
        )

        expected_dir = Path(temp_output_dir) / "charts"
        assert result.parent == expected_dir, f"Expected {expected_dir}, got {result.parent}"

    def test_creates_directory_if_missing(self, sample_year_data, monkeypatch):
        """Test that function creates output directory if it does not exist."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return sample_year_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        with tempfile.TemporaryDirectory() as tmpdir:
            new_output_dir = os.path.join(tmpdir, "new_output_dir")
            assert not os.path.exists(new_output_dir)

            result = generate_price_chart(
                ticker="AAPL",
                start_date="2024-01-01",
                end_date="2024-12-31",
                output_dir=new_output_dir
            )

            assert result.exists()
            assert os.path.exists(os.path.join(new_output_dir, "charts"))


class TestGeneratePriceChartDataHandling:
    """Tests for data loading and error handling."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_raises_error_for_missing_data(self, temp_output_dir, monkeypatch):
        """Test that function raises error if data is missing (not silent failure)."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return pd.DataFrame()  # Empty data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        with pytest.raises(ValueError, match="[Nn]o data|[Ee]mpty|[Mm]issing"):
            generate_price_chart(
                ticker="INVALID_TICKER",
                start_date="2024-01-01",
                end_date="2024-12-31",
                output_dir=temp_output_dir
            )

    def test_raises_error_for_insufficient_data(self, temp_output_dir, monkeypatch):
        """Test that function raises error if data has too few rows for indicators."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        # Create minimal data (less than 200 days for SMA200)
        short_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [101, 102, 103],
            'Low': [99, 100, 101],
            'Close': [100.5, 101.5, 102.5],
            'Volume': [1000000, 1000000, 1000000]
        }, index=pd.date_range(start='2024-01-01', periods=3, freq='B'))

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return short_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        with pytest.raises(ValueError, match="[Ii]nsufficient|[Nn]ot enough|[Mm]inimum"):
            generate_price_chart(
                ticker="AAPL",
                start_date="2024-01-01",
                end_date="2024-01-05",
                output_dir=temp_output_dir
            )


class TestGeneratePriceChartVisuals:
    """Tests for visual output characteristics."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_year_data(self):
        """Create sample ~1 year of OHLCV data."""
        days = 252
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.random.uniform(0, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    def test_image_has_reasonable_dimensions(self, temp_output_dir, sample_year_data, monkeypatch):
        """Test that generated image has reasonable dimensions (not too small/large)."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return sample_year_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        result = generate_price_chart(
            ticker="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            output_dir=temp_output_dir
        )

        img = Image.open(result)
        width, height = img.size
        img.close()  # Close file to allow cleanup on Windows

        # Chart should be readable - at least 800x600
        assert width >= 800, f"Width too small: {width}"
        assert height >= 600, f"Height too small: {height}"

        # Not excessively large (memory concerns)
        assert width <= 4000, f"Width too large: {width}"
        assert height <= 3000, f"Height too large: {height}"

    def test_image_file_size_reasonable(self, temp_output_dir, sample_year_data, monkeypatch):
        """Test that image file size is reasonable (not corrupted/empty)."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return sample_year_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        result = generate_price_chart(
            ticker="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            output_dir=temp_output_dir
        )

        file_size = result.stat().st_size
        # Should be at least 10KB for a meaningful chart
        assert file_size > 10000, f"File too small ({file_size} bytes), may be corrupted"
        # Should not be excessively large
        assert file_size < 5000000, f"File too large ({file_size} bytes)"


class TestGeneratePriceChartWithDataframe:
    """Tests for generate_price_chart_from_dataframe function (direct data input)."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_year_data(self):
        """Create sample ~1 year of OHLCV data."""
        days = 252
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.random.uniform(0, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    def test_function_exists(self):
        """Test that generate_price_chart_from_dataframe function exists."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe
        assert callable(generate_price_chart_from_dataframe)

    def test_accepts_dataframe_directly(self, temp_output_dir, sample_year_data):
        """Test that function accepts DataFrame directly without fetching."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir
        )

        assert isinstance(result, Path)
        assert result.exists()

    def test_creates_chart_with_correct_filename(self, temp_output_dir, sample_year_data):
        """Test that chart is created with correct filename."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        result = generate_price_chart_from_dataframe(
            ticker="GOOGL",
            data=sample_year_data,
            output_dir=temp_output_dir
        )

        assert result.name == "GOOGL_price_chart.png"


class TestTradingViewStyle:
    """Tests for TradingView-like styling."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_year_data(self):
        """Create sample ~1 year of OHLCV data."""
        days = 252
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.random.uniform(0, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    def test_style_parameter_tradingview(self, temp_output_dir, sample_year_data):
        """Test that tradingview style can be specified."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir,
            style="tradingview"
        )

        assert result.exists()

    def test_default_style_is_tradingview(self, temp_output_dir, sample_year_data):
        """Test that default style is tradingview."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        # Call without style parameter
        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir
        )

        assert result.exists()
        # If we had access to the chart internals, we'd verify dark background
        # For now, just verify it works without style parameter


class TestChartIndicators:
    """Tests for chart indicators (SMA, Bollinger Bands)."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_year_data(self):
        """Create sample ~1 year of OHLCV data with enough history for SMA200."""
        days = 300  # More than 200 for SMA200
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.random.uniform(0, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    def test_chart_generation_with_all_indicators(self, temp_output_dir, sample_year_data):
        """Test that chart generates successfully with SMA20, SMA50, SMA200, BB."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        # This test verifies the function completes without error
        # when all indicators are calculated
        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir
        )

        assert result.exists()
        # File should be reasonably sized (indicators add visual complexity)
        assert result.stat().st_size > 10000


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_handles_special_characters_in_ticker(self, temp_output_dir):
        """Test handling of tickers with special characters (e.g., BRK.A)."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        days = 252
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        data = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.random.uniform(0, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)

        result = generate_price_chart_from_dataframe(
            ticker="BRK-A",  # Sanitized version
            data=data,
            output_dir=temp_output_dir
        )

        assert result.exists()
        assert "BRK-A" in result.name

    def test_handles_lowercase_column_names(self, temp_output_dir):
        """Test handling of lowercase column names."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        days = 252
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        # Use lowercase column names
        data = pd.DataFrame({
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'high': prices * (1 + np.random.uniform(0, 0.02, days)),
            'low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)

        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=data,
            output_dir=temp_output_dir
        )

        assert result.exists()

    def test_raises_for_none_dataframe(self, temp_output_dir):
        """Test that passing None as data raises clear error."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        with pytest.raises((ValueError, TypeError)):
            generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=None,
                output_dir=temp_output_dir
            )

    def test_raises_for_missing_required_columns(self, temp_output_dir):
        """Test that missing OHLCV columns raises clear error."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        # Missing 'volume' column
        bad_data = pd.DataFrame({
            'Open': [100, 101],
            'High': [101, 102],
            'Low': [99, 100],
            'Close': [100.5, 101.5]
        }, index=pd.date_range(start='2024-01-01', periods=2, freq='B'))

        with pytest.raises(ValueError, match="[Cc]olumn|[Mm]issing"):
            generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=bad_data,
                output_dir=temp_output_dir
            )


# =============================================================================
# Phase 2 Tests: Trade Markers (IN/OUT)
# =============================================================================

class TestGeneratePriceChartWithTradeMarkers:
    """Tests for Phase 2: Trade marker functionality (IN/OUT markers)."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_year_data(self):
        """Create sample ~1 year of OHLCV data."""
        days = 252
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.random.uniform(0, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    @pytest.fixture
    def sample_trade_log_csv(self, temp_output_dir):
        """Create sample trade_log.csv for testing."""
        trade_log_path = os.path.join(temp_output_dir, 'trade_log.csv')
        trade_data = pd.DataFrame({
            'date': ['2024-03-15', '2024-05-20', '2024-07-10', '2024-09-25'],
            'ticker': ['AAPL', 'AAPL', 'AAPL', 'AAPL'],
            'action': ['ENTRY', 'EXIT', 'ENTRY', 'EXIT'],
            'price': [105.0, 115.0, 112.0, 120.0],
            'shares': [50, 50, 50, 50],
            'reason': ['entry_signal', 'target_reached', 'entry_signal', 'stop_loss'],
            'pnl': [None, 500.0, None, 400.0],
            'capital_after': [94750.0, 100250.0, 94360.0, 100760.0]
        })
        trade_data.to_csv(trade_log_path, index=False)
        return trade_log_path

    def test_generate_price_chart_accepts_trade_log_path(self, temp_output_dir, sample_year_data, monkeypatch):
        """Test that generate_price_chart accepts trade_log_path parameter."""
        from backtest.ticker_charts import generate_price_chart
        import yfinance as yf

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return sample_year_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        # Should not raise TypeError for trade_log_path parameter
        try:
            result = generate_price_chart(
                ticker="AAPL",
                start_date="2024-01-01",
                end_date="2024-12-31",
                output_dir=temp_output_dir,
                trade_log_path=None  # No trade log
            )
        except TypeError as e:
            if "trade_log_path" in str(e):
                pytest.fail(f"trade_log_path parameter not accepted: {e}")
            raise

    def test_generate_price_chart_from_dataframe_accepts_trade_log_path(self, temp_output_dir, sample_year_data):
        """Test that generate_price_chart_from_dataframe accepts trade_log_path."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir,
            trade_log_path=None
        )

        assert isinstance(result, Path)
        assert result.exists()

    def test_chart_with_trade_log_generates_successfully(
        self, temp_output_dir, sample_year_data, sample_trade_log_csv
    ):
        """Test that chart generates with trade_log markers."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir,
            trade_log_path=sample_trade_log_csv
        )

        assert result.exists()
        # File should be larger due to markers
        assert result.stat().st_size > 10000

    def test_chart_without_trade_log_no_error(self, temp_output_dir, sample_year_data):
        """Test that chart generates without trade_log (no errors)."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir,
            trade_log_path=None
        )

        assert result.exists()

    def test_chart_with_nonexistent_trade_log_no_error(self, temp_output_dir, sample_year_data):
        """Test that nonexistent trade_log file does not cause error."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir,
            trade_log_path="/nonexistent/path/trade_log.csv"
        )

        # Should generate chart without markers, not raise error
        assert result.exists()

    def test_chart_with_empty_trade_log_no_error(self, temp_output_dir, sample_year_data):
        """Test that empty trade_log generates chart without error."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        # Create empty trade_log.csv
        empty_trade_log = os.path.join(temp_output_dir, 'empty_trade_log.csv')
        pd.DataFrame(columns=['date', 'ticker', 'action', 'price', 'shares', 'reason', 'pnl', 'capital_after']).to_csv(
            empty_trade_log, index=False
        )

        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir,
            trade_log_path=empty_trade_log
        )

        assert result.exists()

    def test_chart_filters_trade_log_by_ticker(self, temp_output_dir, sample_year_data):
        """Test that only trades for the specified ticker are shown."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        # Create trade_log with multiple tickers
        mixed_trade_log = os.path.join(temp_output_dir, 'mixed_trade_log.csv')
        trade_data = pd.DataFrame({
            'date': ['2024-03-15', '2024-05-20', '2024-04-01', '2024-06-15'],
            'ticker': ['AAPL', 'AAPL', 'GOOGL', 'GOOGL'],
            'action': ['ENTRY', 'EXIT', 'ENTRY', 'EXIT'],
            'price': [105.0, 115.0, 140.0, 150.0],
            'shares': [50, 50, 30, 30],
            'reason': ['entry_signal', 'target_reached', 'entry_signal', 'target_reached'],
            'pnl': [None, 500.0, None, 300.0],
            'capital_after': [94750.0, 100250.0, 95800.0, 100300.0]
        })
        trade_data.to_csv(mixed_trade_log, index=False)

        # Generate chart for AAPL only
        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir,
            trade_log_path=mixed_trade_log
        )

        assert result.exists()
        # We can't easily verify marker filtering visually in unit tests,
        # but the function should complete without error

    def test_multiple_trades_same_ticker_all_visible(
        self, temp_output_dir, sample_year_data
    ):
        """Test that multiple trades for same ticker all appear on chart."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe

        # Create trade_log with 5 trades for same ticker
        multi_trade_log = os.path.join(temp_output_dir, 'multi_trade_log.csv')
        trade_data = pd.DataFrame({
            'date': ['2024-02-15', '2024-03-20', '2024-05-10', '2024-06-25', '2024-08-15',
                     '2024-03-01', '2024-04-15', '2024-05-30', '2024-07-20', '2024-09-10'],
            'ticker': ['AAPL'] * 10,
            'action': ['ENTRY', 'EXIT', 'ENTRY', 'EXIT', 'ENTRY',
                       'EXIT', 'ENTRY', 'EXIT', 'ENTRY', 'EXIT'],
            'price': [100, 110, 105, 115, 110, 108, 112, 120, 115, 125],
            'shares': [50] * 10,
            'reason': ['entry_signal', 'target_reached'] * 5,
            'pnl': [None, 500.0, None, 500.0, None, -100.0, None, 400.0, None, 500.0],
            'capital_after': [95000, 100500, 95250, 100750, 95500, 100400, 95000, 100400, 95250, 100750]
        })
        trade_data.to_csv(multi_trade_log, index=False)

        result = generate_price_chart_from_dataframe(
            ticker="AAPL",
            data=sample_year_data,
            output_dir=temp_output_dir,
            trade_log_path=multi_trade_log
        )

        assert result.exists()
        # File should be reasonably sized (5 ENTRY + 5 EXIT markers)
        assert result.stat().st_size > 10000


class TestGenerateTopBottomCharts:
    """Tests for Phase 2: Top/Bottom chart generation functionality."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_year_data(self):
        """Create sample ~1 year of OHLCV data."""
        days = 252
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=days, freq='B')

        base_price = 100
        returns = np.random.normal(0.0005, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.random.uniform(0, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        return df

    @pytest.fixture
    def sample_ticker_stats_csv(self, temp_output_dir):
        """Create sample ticker_stats.csv for testing."""
        ticker_stats_path = os.path.join(temp_output_dir, 'ticker_stats.csv')
        stats_data = pd.DataFrame({
            'ticker': ['NVDA', 'AAPL', 'MSFT', 'META', 'GOOGL', 'AMZN', 'TSLA', 'AMD', 'INTC', 'IBM'],
            'total_pnl': [1500.0, 1000.0, 800.0, 600.0, 400.0, -100.0, -300.0, -500.0, -700.0, -900.0],
            'trade_count': [3, 5, 2, 4, 3, 2, 4, 3, 2, 1]
        })
        stats_data.to_csv(ticker_stats_path, index=False)
        return ticker_stats_path

    @pytest.fixture
    def sample_trade_log_csv(self, temp_output_dir):
        """Create sample trade_log.csv for testing."""
        trade_log_path = os.path.join(temp_output_dir, 'trade_log.csv')
        # Create trade entries for all tickers
        tickers = ['NVDA', 'AAPL', 'MSFT', 'META', 'GOOGL', 'AMZN', 'TSLA', 'AMD', 'INTC', 'IBM']
        rows = []
        for ticker in tickers:
            rows.append({
                'date': '2024-03-15', 'ticker': ticker, 'action': 'ENTRY',
                'price': 100.0, 'shares': 50, 'reason': 'entry_signal',
                'pnl': None, 'capital_after': 95000.0
            })
            rows.append({
                'date': '2024-06-20', 'ticker': ticker, 'action': 'EXIT',
                'price': 110.0, 'shares': 50, 'reason': 'target_reached',
                'pnl': 500.0, 'capital_after': 100500.0
            })
        trade_data = pd.DataFrame(rows)
        trade_data.to_csv(trade_log_path, index=False)
        return trade_log_path

    def test_function_exists(self):
        """Test that generate_top_bottom_charts function exists."""
        from backtest.ticker_charts import generate_top_bottom_charts
        assert callable(generate_top_bottom_charts)

    def test_function_signature(self, temp_output_dir, sample_ticker_stats_csv, sample_trade_log_csv):
        """Test that function accepts required parameters."""
        from backtest.ticker_charts import generate_top_bottom_charts

        # Should not raise TypeError
        try:
            result = generate_top_bottom_charts(
                ticker_stats_path=sample_ticker_stats_csv,
                trade_log_path=sample_trade_log_csv,
                output_dir=temp_output_dir,
                top_n=5,
                bottom_n=5
            )
        except TypeError as e:
            pytest.fail(f"Function signature error: {e}")
        except Exception:
            pass  # Other errors are OK for signature test

    def test_returns_list_of_paths(self, temp_output_dir, sample_ticker_stats_csv, sample_trade_log_csv, monkeypatch):
        """Test that function returns a list of Path objects."""
        from backtest.ticker_charts import generate_top_bottom_charts
        import yfinance as yf

        # Mock yfinance for all tickers
        def mock_ticker_init(self, ticker):
            self.ticker = ticker

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
                mock_ticker_init(self, ticker)

            def history(self, start=None, end=None, period=None):
                return mock_history(self, start, end, period)

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        result = generate_top_bottom_charts(
            ticker_stats_path=sample_ticker_stats_csv,
            trade_log_path=sample_trade_log_csv,
            output_dir=temp_output_dir,
            top_n=2,
            bottom_n=2
        )

        assert isinstance(result, list)
        # Should return 4 paths (2 top + 2 bottom)
        assert len(result) == 4
        for path in result:
            assert isinstance(path, Path)

    def test_selects_correct_top_n_tickers(self, temp_output_dir, sample_ticker_stats_csv, sample_trade_log_csv, monkeypatch):
        """Test that correct top N tickers are selected by P&L."""
        from backtest.ticker_charts import generate_top_bottom_charts
        import yfinance as yf

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

        result = generate_top_bottom_charts(
            ticker_stats_path=sample_ticker_stats_csv,
            trade_log_path=sample_trade_log_csv,
            output_dir=temp_output_dir,
            top_n=3,
            bottom_n=0
        )

        # Top 3 should be NVDA, AAPL, MSFT (highest P&L)
        filenames = [p.name for p in result]
        assert any('NVDA' in f for f in filenames)
        assert any('AAPL' in f for f in filenames)
        assert any('MSFT' in f for f in filenames)

    def test_selects_correct_bottom_n_tickers(self, temp_output_dir, sample_ticker_stats_csv, sample_trade_log_csv, monkeypatch):
        """Test that correct bottom N tickers are selected by P&L."""
        from backtest.ticker_charts import generate_top_bottom_charts
        import yfinance as yf

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

        result = generate_top_bottom_charts(
            ticker_stats_path=sample_ticker_stats_csv,
            trade_log_path=sample_trade_log_csv,
            output_dir=temp_output_dir,
            top_n=0,
            bottom_n=3
        )

        # Bottom 3 should be IBM, INTC, AMD (lowest P&L)
        filenames = [p.name for p in result]
        assert any('IBM' in f for f in filenames)
        assert any('INTC' in f for f in filenames)
        assert any('AMD' in f for f in filenames)

    def test_output_filename_pattern_top(self, temp_output_dir, sample_ticker_stats_csv, sample_trade_log_csv, monkeypatch):
        """Test that top tickers have correct filename pattern: top_01_TICKER.png."""
        from backtest.ticker_charts import generate_top_bottom_charts
        import yfinance as yf

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

        result = generate_top_bottom_charts(
            ticker_stats_path=sample_ticker_stats_csv,
            trade_log_path=sample_trade_log_csv,
            output_dir=temp_output_dir,
            top_n=2,
            bottom_n=0
        )

        filenames = [p.name for p in result]
        # Should have top_01_NVDA.png, top_02_AAPL.png
        assert 'top_01_NVDA.png' in filenames
        assert 'top_02_AAPL.png' in filenames

    def test_output_filename_pattern_bottom(self, temp_output_dir, sample_ticker_stats_csv, sample_trade_log_csv, monkeypatch):
        """Test that bottom tickers have correct filename pattern: bottom_01_TICKER.png."""
        from backtest.ticker_charts import generate_top_bottom_charts
        import yfinance as yf

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

        result = generate_top_bottom_charts(
            ticker_stats_path=sample_ticker_stats_csv,
            trade_log_path=sample_trade_log_csv,
            output_dir=temp_output_dir,
            top_n=0,
            bottom_n=2
        )

        filenames = [p.name for p in result]
        # Bottom tickers from stats sorted descending: tail(2) gives INTC(-700), IBM(-900)
        # So bottom_01 = INTC (first in tail), bottom_02 = IBM (second in tail)
        assert 'bottom_01_INTC.png' in filenames
        assert 'bottom_02_IBM.png' in filenames

    def test_charts_saved_to_charts_subdirectory(self, temp_output_dir, sample_ticker_stats_csv, sample_trade_log_csv, monkeypatch):
        """Test that charts are saved in output_dir/charts/."""
        from backtest.ticker_charts import generate_top_bottom_charts
        import yfinance as yf

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

        result = generate_top_bottom_charts(
            ticker_stats_path=sample_ticker_stats_csv,
            trade_log_path=sample_trade_log_csv,
            output_dir=temp_output_dir,
            top_n=1,
            bottom_n=1
        )

        expected_dir = Path(temp_output_dir) / "charts"
        for path in result:
            assert path.parent == expected_dir

    def test_handles_fewer_tickers_than_requested(self, temp_output_dir):
        """Test handling when fewer tickers exist than requested."""
        from backtest.ticker_charts import generate_top_bottom_charts

        # Create ticker_stats with only 3 tickers
        ticker_stats_path = os.path.join(temp_output_dir, 'small_ticker_stats.csv')
        stats_data = pd.DataFrame({
            'ticker': ['AAPL', 'GOOGL', 'MSFT'],
            'total_pnl': [1000.0, 500.0, -200.0],
            'trade_count': [2, 1, 1]
        })
        stats_data.to_csv(ticker_stats_path, index=False)

        trade_log_path = os.path.join(temp_output_dir, 'trade_log.csv')
        pd.DataFrame({
            'date': ['2024-03-15'] * 3,
            'ticker': ['AAPL', 'GOOGL', 'MSFT'],
            'action': ['EXIT'] * 3,
            'price': [110.0] * 3,
            'shares': [50] * 3,
            'reason': ['target_reached'] * 3,
            'pnl': [1000.0, 500.0, -200.0],
            'capital_after': [100000.0] * 3
        }).to_csv(trade_log_path, index=False)

        # Request more than available - should not raise error
        try:
            result = generate_top_bottom_charts(
                ticker_stats_path=ticker_stats_path,
                trade_log_path=trade_log_path,
                output_dir=temp_output_dir,
                top_n=5,  # Only 3 exist
                bottom_n=5  # Only 3 exist
            )
            # Should return up to available tickers
            # Could be 3 (all) or 6 (top 3 + bottom 3 with overlap)
            assert len(result) <= 6
        except Exception as e:
            pytest.fail(f"Should handle fewer tickers gracefully: {e}")

    def test_handles_empty_ticker_stats(self, temp_output_dir):
        """Test handling of empty ticker_stats.csv."""
        from backtest.ticker_charts import generate_top_bottom_charts

        # Create empty ticker_stats
        ticker_stats_path = os.path.join(temp_output_dir, 'empty_ticker_stats.csv')
        pd.DataFrame(columns=['ticker', 'total_pnl', 'trade_count']).to_csv(ticker_stats_path, index=False)

        trade_log_path = os.path.join(temp_output_dir, 'trade_log.csv')
        pd.DataFrame(columns=['date', 'ticker', 'action', 'price', 'shares', 'reason', 'pnl', 'capital_after']).to_csv(
            trade_log_path, index=False
        )

        result = generate_top_bottom_charts(
            ticker_stats_path=ticker_stats_path,
            trade_log_path=trade_log_path,
            output_dir=temp_output_dir,
            top_n=5,
            bottom_n=5
        )

        # Should return empty list
        assert result == []


class TestParseTradeLog:
    """Tests for trade log parsing utility function."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_parse_trade_log_function_exists(self):
        """Test that _parse_trade_log function exists."""
        from backtest.ticker_charts import _parse_trade_log
        assert callable(_parse_trade_log)

    def test_parse_trade_log_filters_by_ticker(self, temp_output_dir):
        """Test that trade log is filtered by ticker."""
        from backtest.ticker_charts import _parse_trade_log

        trade_log_path = os.path.join(temp_output_dir, 'trade_log.csv')
        trade_data = pd.DataFrame({
            'date': ['2024-03-15', '2024-05-20', '2024-04-01', '2024-06-15'],
            'ticker': ['AAPL', 'AAPL', 'GOOGL', 'GOOGL'],
            'action': ['ENTRY', 'EXIT', 'ENTRY', 'EXIT'],
            'price': [105.0, 115.0, 140.0, 150.0],
            'shares': [50, 50, 30, 30],
            'reason': ['entry_signal', 'target_reached', 'entry_signal', 'target_reached'],
            'pnl': [None, 500.0, None, 300.0],
            'capital_after': [94750.0, 100250.0, 95800.0, 100300.0]
        })
        trade_data.to_csv(trade_log_path, index=False)

        entry_dates, exit_dates = _parse_trade_log(trade_log_path, 'AAPL')

        assert len(entry_dates) == 1
        assert len(exit_dates) == 1

    def test_parse_trade_log_returns_datetime_objects(self, temp_output_dir):
        """Test that parsed dates are datetime-compatible."""
        from backtest.ticker_charts import _parse_trade_log

        trade_log_path = os.path.join(temp_output_dir, 'trade_log.csv')
        trade_data = pd.DataFrame({
            'date': ['2024-03-15', '2024-05-20'],
            'ticker': ['AAPL', 'AAPL'],
            'action': ['ENTRY', 'EXIT'],
            'price': [105.0, 115.0],
            'shares': [50, 50],
            'reason': ['entry_signal', 'target_reached'],
            'pnl': [None, 500.0],
            'capital_after': [94750.0, 100250.0]
        })
        trade_data.to_csv(trade_log_path, index=False)

        entry_dates, exit_dates = _parse_trade_log(trade_log_path, 'AAPL')

        # Should be usable as index for DataFrame lookups
        assert hasattr(entry_dates[0], 'year')
        assert hasattr(exit_dates[0], 'year')

    def test_parse_trade_log_handles_missing_file(self, temp_output_dir):
        """Test graceful handling of missing trade_log file."""
        from backtest.ticker_charts import _parse_trade_log

        entry_dates, exit_dates = _parse_trade_log('/nonexistent/path.csv', 'AAPL')

        assert entry_dates == []
        assert exit_dates == []

    def test_parse_trade_log_handles_empty_file(self, temp_output_dir):
        """Test graceful handling of empty trade_log file."""
        from backtest.ticker_charts import _parse_trade_log

        trade_log_path = os.path.join(temp_output_dir, 'empty_trade_log.csv')
        pd.DataFrame(columns=['date', 'ticker', 'action', 'price']).to_csv(trade_log_path, index=False)

        entry_dates, exit_dates = _parse_trade_log(trade_log_path, 'AAPL')

        assert entry_dates == []
        assert exit_dates == []
