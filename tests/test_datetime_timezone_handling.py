"""
Tests for Datetime Timezone Handling in Chart Generation

TDD Test Suite for the timezone mismatch bug:
- Price data (OHLCV DataFrame index) is timezone-aware (America/New_York)
- Entry/exit timestamps from trade_log.csv are timezone-naive
- This causes "Invalid comparison between dtype=datetime64[ns, America/New_York] and Timestamp"

SOLUTION:
- When parsing trade_log.csv dates, localize them to America/New_York
- Ensure OHLCV dataframe index is also America/New_York
- NEVER strip timezone information from price data

Test Cases:
1. _parse_trade_log should return timezone-aware timestamps (America/New_York)
2. normalize_timestamp utility should localize tz-naive to America/New_York
3. normalize_timestamp should convert other timezones to America/New_York
4. _create_trade_markers should work with tz-aware OHLCV data
5. Integration test: chart generation with tz-aware data and trade markers
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import tempfile
import os
import pytz

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))


class TestNormalizeTimestamp:
    """Tests for normalize_timestamp utility function."""

    def test_normalize_timestamp_function_exists(self):
        """Test that normalize_timestamp utility function exists."""
        from backtest.ticker_charts import normalize_timestamp
        assert callable(normalize_timestamp)

    def test_normalize_naive_timestamp_to_america_new_york(self):
        """Test that timezone-naive timestamp is localized to America/New_York."""
        from backtest.ticker_charts import normalize_timestamp

        naive_ts = pd.Timestamp('2024-03-15')
        result = normalize_timestamp(naive_ts)

        assert result.tzinfo is not None
        assert str(result.tzinfo) == 'America/New_York' or 'America/New_York' in str(result.tz)

    def test_normalize_utc_timestamp_to_america_new_york(self):
        """Test that UTC timestamp is converted to America/New_York."""
        from backtest.ticker_charts import normalize_timestamp

        utc_ts = pd.Timestamp('2024-03-15 14:30:00', tz='UTC')
        result = normalize_timestamp(utc_ts)

        assert result.tzinfo is not None
        # Result should be in America/New_York timezone
        assert 'America/New_York' in str(result.tz) or str(result.tzinfo) == 'America/New_York'

    def test_normalize_america_new_york_timestamp_unchanged(self):
        """Test that America/New_York timestamp remains unchanged."""
        from backtest.ticker_charts import normalize_timestamp

        ny_tz = pytz.timezone('America/New_York')
        ny_ts = pd.Timestamp('2024-03-15 10:00:00', tz=ny_tz)
        result = normalize_timestamp(ny_ts)

        assert result.tzinfo is not None
        # Should still be America/New_York
        assert 'America/New_York' in str(result.tz) or str(result.tzinfo) == 'America/New_York'

    def test_normalize_datetime_string_to_america_new_york(self):
        """Test that datetime string is parsed and localized to America/New_York."""
        from backtest.ticker_charts import normalize_timestamp

        date_str = '2024-03-15'
        result = normalize_timestamp(date_str)

        assert isinstance(result, pd.Timestamp)
        assert result.tzinfo is not None

    def test_normalize_datetime_object_to_america_new_york(self):
        """Test that datetime object is localized to America/New_York."""
        from backtest.ticker_charts import normalize_timestamp

        dt = datetime(2024, 3, 15, 10, 30, 0)
        result = normalize_timestamp(dt)

        assert isinstance(result, pd.Timestamp)
        assert result.tzinfo is not None


class TestParseTradeLogTimezoneAware:
    """Tests for _parse_trade_log returning timezone-aware timestamps."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_trade_log_csv(self, temp_output_dir):
        """Create sample trade_log.csv with timezone-naive date strings."""
        trade_log_path = os.path.join(temp_output_dir, 'trade_log.csv')
        trade_data = pd.DataFrame({
            'date': ['2024-03-15', '2024-05-20'],  # Naive date strings
            'ticker': ['AAPL', 'AAPL'],
            'action': ['ENTRY', 'EXIT'],
            'price': [105.0, 115.0],
            'shares': [50, 50],
            'reason': ['entry_signal', 'target_reached'],
            'pnl': [None, 500.0],
            'capital_after': [94750.0, 100250.0]
        })
        trade_data.to_csv(trade_log_path, index=False)
        return trade_log_path

    def test_parse_trade_log_returns_timezone_aware_timestamps(self, sample_trade_log_csv):
        """Test that _parse_trade_log returns timezone-aware timestamps."""
        from backtest.ticker_charts import _parse_trade_log

        entry_dates, exit_dates = _parse_trade_log(sample_trade_log_csv, 'AAPL')

        # Entry dates should be timezone-aware
        assert len(entry_dates) == 1
        assert entry_dates[0].tzinfo is not None, "Entry date should be timezone-aware"

        # Exit dates should be timezone-aware
        assert len(exit_dates) == 1
        assert exit_dates[0].tzinfo is not None, "Exit date should be timezone-aware"

    def test_parse_trade_log_returns_america_new_york_timezone(self, sample_trade_log_csv):
        """Test that _parse_trade_log returns America/New_York timezone."""
        from backtest.ticker_charts import _parse_trade_log

        entry_dates, exit_dates = _parse_trade_log(sample_trade_log_csv, 'AAPL')

        # Check timezone is America/New_York
        entry_tz = str(entry_dates[0].tz) if hasattr(entry_dates[0], 'tz') else str(entry_dates[0].tzinfo)
        exit_tz = str(exit_dates[0].tz) if hasattr(exit_dates[0], 'tz') else str(exit_dates[0].tzinfo)

        assert 'America/New_York' in entry_tz or entry_tz == 'America/New_York'
        assert 'America/New_York' in exit_tz or exit_tz == 'America/New_York'


class TestCreateTradeMarkersTimezoneAware:
    """Tests for _create_trade_markers with timezone-aware data."""

    @pytest.fixture
    def tz_aware_ohlcv_data(self):
        """Create sample OHLCV data with timezone-aware index (America/New_York)."""
        days = 100
        np.random.seed(42)

        # Create timezone-aware DatetimeIndex (America/New_York)
        ny_tz = pytz.timezone('America/New_York')
        dates = pd.date_range(
            start='2024-01-01',
            periods=days,
            freq='B',
            tz=ny_tz
        )

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

    def test_create_trade_markers_with_tz_aware_data_and_dates(self, tz_aware_ohlcv_data):
        """Test _create_trade_markers works with tz-aware OHLCV data and tz-aware trade dates."""
        from backtest.ticker_charts import _create_trade_markers, normalize_timestamp, MPLFINANCE_AVAILABLE

        if not MPLFINANCE_AVAILABLE:
            pytest.skip("mplfinance not installed")

        # Create timezone-aware entry/exit dates (America/New_York)
        ny_tz = pytz.timezone('America/New_York')
        entry_dates = [pd.Timestamp('2024-02-15', tz=ny_tz)]
        exit_dates = [pd.Timestamp('2024-03-20', tz=ny_tz)]

        # This should NOT raise "Invalid comparison" error
        try:
            addplots = _create_trade_markers(tz_aware_ohlcv_data, entry_dates, exit_dates)
            # Should return list of addplots (could be empty if dates not in index)
            assert isinstance(addplots, list)
        except TypeError as e:
            if "Invalid comparison" in str(e):
                pytest.fail(f"Timezone mismatch error: {e}")
            raise

    def test_create_trade_markers_handles_date_lookup_with_tz(self, tz_aware_ohlcv_data):
        """Test that trade markers correctly find dates in tz-aware index."""
        from backtest.ticker_charts import _create_trade_markers, MPLFINANCE_AVAILABLE

        if not MPLFINANCE_AVAILABLE:
            pytest.skip("mplfinance not installed")

        # Use a date we know is in the data
        ny_tz = pytz.timezone('America/New_York')
        # Get a date that exists in the index
        valid_date = tz_aware_ohlcv_data.index[50]
        entry_dates = [valid_date]
        exit_dates = []

        # Should not raise any error
        addplots = _create_trade_markers(tz_aware_ohlcv_data, entry_dates, exit_dates)
        # Should have at least one addplot for the entry marker
        assert len(addplots) >= 1


class TestDatetimeComparisonSafety:
    """Tests for safe datetime comparisons between tz-aware and tz-naive."""

    def test_tz_aware_index_with_tz_aware_timestamp_comparison(self):
        """Test that tz-aware index can be compared with tz-aware timestamp."""
        ny_tz = pytz.timezone('America/New_York')

        # Create tz-aware index
        dates = pd.date_range('2024-01-01', periods=10, freq='B', tz=ny_tz)
        df = pd.DataFrame({'value': range(10)}, index=dates)

        # Create tz-aware timestamp
        ts = pd.Timestamp('2024-01-03', tz=ny_tz)

        # This should work without error
        result = df.index >= ts
        assert isinstance(result, pd.Series) or isinstance(result, np.ndarray)

    def test_tz_aware_index_with_tz_naive_timestamp_fails(self):
        """Test that tz-aware index compared with tz-naive timestamp raises error."""
        ny_tz = pytz.timezone('America/New_York')

        # Create tz-aware index
        dates = pd.date_range('2024-01-01', periods=10, freq='B', tz=ny_tz)
        df = pd.DataFrame({'value': range(10)}, index=dates)

        # Create tz-naive timestamp
        naive_ts = pd.Timestamp('2024-01-03')

        # This should raise TypeError
        with pytest.raises(TypeError):
            _ = df.index >= naive_ts

    def test_timestamp_in_tz_aware_index_requires_tz_match(self):
        """Test that 'in' operator requires timezone match."""
        ny_tz = pytz.timezone('America/New_York')

        # Create tz-aware index
        dates = pd.date_range('2024-01-01', periods=10, freq='B', tz=ny_tz)
        df = pd.DataFrame({'value': range(10)}, index=dates)

        # tz-aware timestamp should work
        tz_aware_ts = pd.Timestamp('2024-01-03', tz=ny_tz)
        # Note: exact date match may not work due to time component, but no error
        try:
            _ = tz_aware_ts in df.index
        except TypeError:
            pytest.fail("tz-aware timestamp should not raise TypeError")


class TestChartGenerationIntegrationTimezone:
    """Integration tests for chart generation with timezone handling."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def tz_aware_ohlcv_data(self):
        """Create sample OHLCV data with timezone-aware index (America/New_York)."""
        days = 252
        np.random.seed(42)

        # Create timezone-aware DatetimeIndex (America/New_York)
        ny_tz = pytz.timezone('America/New_York')
        dates = pd.date_range(
            start='2024-01-01',
            periods=days,
            freq='B',
            tz=ny_tz
        )

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
        """Create sample trade_log.csv with timezone-naive date strings (as saved by TradeLogger)."""
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

    def test_chart_generation_with_tz_aware_data_and_trade_log(
        self, temp_output_dir, tz_aware_ohlcv_data, sample_trade_log_csv
    ):
        """Test that chart generation works with tz-aware OHLCV data and trade_log.csv."""
        from backtest.ticker_charts import generate_price_chart_from_dataframe, MPLFINANCE_AVAILABLE

        if not MPLFINANCE_AVAILABLE:
            pytest.skip("mplfinance not installed")

        # This should NOT raise "Invalid comparison" error
        try:
            result = generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=tz_aware_ohlcv_data,
                output_dir=temp_output_dir,
                trade_log_path=sample_trade_log_csv
            )
            assert result.exists()
        except TypeError as e:
            if "Invalid comparison" in str(e):
                pytest.fail(f"Timezone mismatch error during chart generation: {e}")
            raise

    def test_chart_generation_preserves_tz_aware_index(
        self, temp_output_dir, tz_aware_ohlcv_data
    ):
        """Test that chart generation does not strip timezone from OHLCV data."""
        from backtest.ticker_charts import _normalize_dataframe

        # Normalize should preserve timezone
        normalized = _normalize_dataframe(tz_aware_ohlcv_data)

        # Index should still be timezone-aware
        assert normalized.index.tz is not None, "Timezone should be preserved after normalization"


class TestYFinanceDataTimezone:
    """Tests verifying yfinance data timezone behavior."""

    def test_yfinance_returns_tz_aware_data(self, monkeypatch):
        """Test that yfinance returns timezone-aware data (America/New_York)."""
        # This test documents the expected yfinance behavior
        # yfinance returns data with America/New_York timezone

        try:
            import yfinance as yf
        except ImportError:
            pytest.skip("yfinance not installed")

        # Mock yfinance to return tz-aware data (as it actually does)
        ny_tz = pytz.timezone('America/New_York')
        days = 50
        dates = pd.date_range('2024-01-01', periods=days, freq='B', tz=ny_tz)
        mock_data = pd.DataFrame({
            'Open': [100] * days,
            'High': [101] * days,
            'Low': [99] * days,
            'Close': [100.5] * days,
            'Volume': [1000000] * days
        }, index=dates)

        class MockTicker:
            def __init__(self, ticker):
                self.ticker = ticker

            def history(self, start=None, end=None, period=None):
                return mock_data

        monkeypatch.setattr(yf, 'Ticker', MockTicker)

        stock = yf.Ticker('AAPL')
        data = stock.history(start='2024-01-01', end='2024-03-01')

        # Verify data is timezone-aware
        assert data.index.tz is not None, "yfinance data should be timezone-aware"


class TestEdgeCasesTimezone:
    """Edge case tests for timezone handling."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_trade_date_not_in_ohlcv_index_no_error(self, temp_output_dir):
        """Test that trade dates not in OHLCV index do not cause errors."""
        from backtest.ticker_charts import _create_trade_markers, MPLFINANCE_AVAILABLE

        if not MPLFINANCE_AVAILABLE:
            pytest.skip("mplfinance not installed")

        ny_tz = pytz.timezone('America/New_York')

        # Create OHLCV data for January only
        dates = pd.date_range('2024-01-01', periods=20, freq='B', tz=ny_tz)
        df = pd.DataFrame({
            'Open': [100] * 20,
            'High': [101] * 20,
            'Low': [99] * 20,
            'Close': [100.5] * 20,
            'Volume': [1000000] * 20
        }, index=dates)

        # Trade dates in March (not in OHLCV data)
        entry_dates = [pd.Timestamp('2024-03-15', tz=ny_tz)]
        exit_dates = [pd.Timestamp('2024-03-20', tz=ny_tz)]

        # Should not raise error, just return empty or find closest
        addplots = _create_trade_markers(df, entry_dates, exit_dates)
        assert isinstance(addplots, list)

    def test_empty_trade_dates_no_error(self, temp_output_dir):
        """Test that empty trade dates list does not cause errors."""
        from backtest.ticker_charts import _create_trade_markers, MPLFINANCE_AVAILABLE

        if not MPLFINANCE_AVAILABLE:
            pytest.skip("mplfinance not installed")

        ny_tz = pytz.timezone('America/New_York')
        dates = pd.date_range('2024-01-01', periods=20, freq='B', tz=ny_tz)
        df = pd.DataFrame({
            'Open': [100] * 20,
            'High': [101] * 20,
            'Low': [99] * 20,
            'Close': [100.5] * 20,
            'Volume': [1000000] * 20
        }, index=dates)

        # Empty trade dates
        entry_dates = []
        exit_dates = []

        addplots = _create_trade_markers(df, entry_dates, exit_dates)
        assert addplots == []

    def test_mixed_timezone_dates_handled(self, temp_output_dir):
        """Test handling when trade dates have different timezones."""
        from backtest.ticker_charts import normalize_timestamp

        # Different source timezones
        utc_ts = pd.Timestamp('2024-03-15 14:30:00', tz='UTC')
        london_ts = pd.Timestamp('2024-03-15 14:30:00', tz='Europe/London')
        naive_ts = pd.Timestamp('2024-03-15')

        # All should be normalized to America/New_York
        utc_result = normalize_timestamp(utc_ts)
        london_result = normalize_timestamp(london_ts)
        naive_result = normalize_timestamp(naive_ts)

        # All should have America/New_York timezone
        for result in [utc_result, london_result, naive_result]:
            assert result.tzinfo is not None
            tz_str = str(result.tz) if hasattr(result, 'tz') else str(result.tzinfo)
            assert 'America/New_York' in tz_str or tz_str == 'America/New_York'
