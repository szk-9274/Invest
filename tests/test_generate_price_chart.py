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
