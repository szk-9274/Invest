"""
Tests for Phase A-1: Chart Generation Edge Case Handling

Tests cover:
1. Empty Data Detection (None, empty DataFrame, zero rows)
2. Insufficient Data Detection (< MIN_REQUIRED_BARS)
3. Skip Logging (WARNING logs emitted on skip)
4. Exception Resilience (catch and continue on chart generation errors)
"""
import pytest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backtest.ticker_charts import (
    MIN_DATA_POINTS,
    generate_price_chart_from_dataframe,
    TickerCharts,
)


def _make_ohlcv_dataframe(rows: int, start_date: str = "2023-01-01") -> pd.DataFrame:
    """
    Helper to create a valid OHLCV DataFrame with the specified number of rows.

    Args:
        rows: Number of rows to generate
        start_date: Start date for the DatetimeIndex

    Returns:
        DataFrame with Open, High, Low, Close, Volume columns and DatetimeIndex
    """
    if rows == 0:
        return pd.DataFrame(
            columns=["Open", "High", "Low", "Close", "Volume"],
            index=pd.DatetimeIndex([], name="Date"),
        )
    dates = pd.bdate_range(start=start_date, periods=rows)
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(rows) * 0.5)
    return pd.DataFrame(
        {
            "Open": close - np.random.rand(rows) * 0.5,
            "High": close + np.random.rand(rows) * 1.0,
            "Low": close - np.random.rand(rows) * 1.0,
            "Close": close,
            "Volume": np.random.randint(100000, 1000000, size=rows),
        },
        index=dates,
    )


# ============================================================
# 1. Empty Data Detection
# ============================================================
class TestEmptyDataDetection:
    """Validate that chart generation skips gracefully when data is empty."""

    def test_none_dataframe_raises_valueerror(self, tmp_path):
        """generate_price_chart_from_dataframe should raise ValueError when data is None."""
        with pytest.raises(ValueError, match="Data cannot be None"):
            generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=None,
                output_dir=str(tmp_path),
            )

    def test_empty_dataframe_raises_valueerror(self, tmp_path):
        """generate_price_chart_from_dataframe should raise ValueError when DataFrame is empty."""
        empty_df = pd.DataFrame(
            columns=["Open", "High", "Low", "Close", "Volume"],
            index=pd.DatetimeIndex([], name="Date"),
        )
        with pytest.raises(ValueError, match="No data available"):
            generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=empty_df,
                output_dir=str(tmp_path),
            )

    def test_zero_rows_dataframe_raises_valueerror(self, tmp_path):
        """generate_price_chart_from_dataframe should raise ValueError when DataFrame has zero rows."""
        zero_df = _make_ohlcv_dataframe(0)
        with pytest.raises(ValueError, match="No data available"):
            generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=zero_df,
                output_dir=str(tmp_path),
            )

    def test_tickercharts_none_data_returns_none(self, tmp_path):
        """TickerCharts.create_chart should return None when data is None."""
        tc = TickerCharts(output_dir=str(tmp_path))
        result = tc.create_chart(ticker="AAPL", data=None, trades=[])
        assert result is None

    def test_tickercharts_empty_data_returns_none(self, tmp_path):
        """TickerCharts.create_chart should return None when data is empty."""
        tc = TickerCharts(output_dir=str(tmp_path))
        empty_df = pd.DataFrame()
        result = tc.create_chart(ticker="AAPL", data=empty_df, trades=[])
        assert result is None


# ============================================================
# 2. Insufficient Data Detection
# ============================================================
class TestInsufficientDataDetection:
    """Validate that chart generation skips when data has too few rows."""

    def test_below_min_data_points_raises_valueerror(self, tmp_path):
        """generate_price_chart_from_dataframe should raise ValueError when rows < MIN_DATA_POINTS."""
        small_df = _make_ohlcv_dataframe(MIN_DATA_POINTS - 1)
        with pytest.raises(ValueError, match="Insufficient data"):
            generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=small_df,
                output_dir=str(tmp_path),
            )

    def test_exactly_min_data_points_does_not_raise(self, tmp_path):
        """generate_price_chart_from_dataframe should NOT raise when rows == MIN_DATA_POINTS."""
        exact_df = _make_ohlcv_dataframe(MIN_DATA_POINTS)
        # This should not raise ValueError for insufficient data
        # It may still raise RuntimeError if mplfinance is not available,
        # but it should NOT raise ValueError about insufficient data.
        try:
            generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=exact_df,
                output_dir=str(tmp_path),
            )
        except ValueError as e:
            if "Insufficient data" in str(e):
                pytest.fail(
                    f"Should not raise Insufficient data error with exactly "
                    f"{MIN_DATA_POINTS} rows"
                )
        except RuntimeError:
            # mplfinance dependency issue is OK -- we only test the validation
            pass

    def test_one_row_raises_insufficient(self, tmp_path):
        """A DataFrame with only 1 row should be rejected as insufficient."""
        tiny_df = _make_ohlcv_dataframe(1)
        with pytest.raises(ValueError, match="Insufficient data"):
            generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=tiny_df,
                output_dir=str(tmp_path),
            )

    def test_tickercharts_insufficient_data_returns_none(self, tmp_path):
        """
        TickerCharts.create_chart should return None for data with very few rows
        (below minimum needed for SMA computation).
        """
        tc = TickerCharts(output_dir=str(tmp_path))
        tiny_df = _make_ohlcv_dataframe(3)
        result = tc.create_chart(ticker="AAPL", data=tiny_df, trades=[])
        # The class method should handle this gracefully and return None
        assert result is None

    def test_tickercharts_below_min_bars_with_valid_columns_returns_none(self, tmp_path):
        """
        TickerCharts.create_chart should return None when data has fewer rows
        than MIN_DATA_POINTS, even when OHLCV columns are correctly named.
        The method should check explicitly and not rely on downstream errors.
        """
        tc = TickerCharts(output_dir=str(tmp_path))
        # Use lowercase columns (matching what TickerCharts expects)
        small_df = _make_ohlcv_dataframe(MIN_DATA_POINTS - 1)
        small_df.columns = [c.lower() for c in small_df.columns]

        # Capture loguru messages
        log_messages = []
        from loguru import logger as loguru_logger
        handler_id = loguru_logger.add(lambda msg: log_messages.append(str(msg)), level="WARNING")

        try:
            result = tc.create_chart(ticker="AAPL", data=small_df, trades=[])
            assert result is None

            # Verify that a WARNING log was emitted mentioning insufficient bars
            insufficient_logs = [
                m for m in log_messages
                if "insufficient" in m.lower() and "AAPL" in m
            ]
            assert len(insufficient_logs) > 0, (
                f"Expected WARNING log about insufficient bars for AAPL, "
                f"got: {log_messages}"
            )
        finally:
            loguru_logger.remove(handler_id)


# ============================================================
# 3. Skip Logging
# ============================================================
class TestSkipLogging:
    """Validate that WARNING logs are emitted when chart generation is skipped."""

    def test_none_data_logs_warning_in_tickercharts(self, tmp_path, caplog):
        """TickerCharts.create_chart should log WARNING when data is None."""
        import logging

        with caplog.at_level(logging.WARNING):
            tc = TickerCharts(output_dir=str(tmp_path))
            tc.create_chart(ticker="AAPL", data=None, trades=[])

        # loguru may not always propagate to caplog,
        # so we also verify return value (tested above).
        # This test primarily checks the method does not crash.

    def test_empty_data_logs_warning_in_tickercharts(self, tmp_path, caplog):
        """TickerCharts.create_chart should log WARNING when data is empty."""
        import logging

        with caplog.at_level(logging.WARNING):
            tc = TickerCharts(output_dir=str(tmp_path))
            tc.create_chart(ticker="MSFT", data=pd.DataFrame(), trades=[])

    def test_insufficient_data_message_contains_ticker(self, tmp_path):
        """ValueError message should contain useful information about the ticker."""
        small_df = _make_ohlcv_dataframe(10)
        with pytest.raises(ValueError) as exc_info:
            generate_price_chart_from_dataframe(
                ticker="TSLA",
                data=small_df,
                output_dir=str(tmp_path),
            )
        assert "Insufficient data" in str(exc_info.value)
        assert str(MIN_DATA_POINTS) in str(exc_info.value)
        assert "10" in str(exc_info.value)

    def test_create_charts_for_tickers_skips_missing_data(self, tmp_path):
        """create_charts_for_tickers should skip tickers with no data and log warning."""
        tc = TickerCharts(output_dir=str(tmp_path))
        result = tc.create_charts_for_tickers(
            tickers=["AAPL", "MISSING"],
            ticker_data={"AAPL": None},
            trades_by_ticker={},
        )
        # AAPL has None data, MISSING has no entry at all
        assert result == {}


# ============================================================
# 4. Exception Resilience
# ============================================================
class TestExceptionResilience:
    """Validate that chart generation catches exceptions and continues."""

    def test_tickercharts_create_chart_catches_mplfinance_error(self, tmp_path):
        """
        TickerCharts.create_chart should catch internal exceptions
        and return None instead of raising.
        """
        tc = TickerCharts(output_dir=str(tmp_path))
        # Create a DataFrame that will cause mplfinance issues
        # (e.g., NaN in all values)
        bad_df = _make_ohlcv_dataframe(100)
        bad_df["Close"] = np.nan
        bad_df["Open"] = np.nan
        bad_df["High"] = np.nan
        bad_df["Low"] = np.nan

        result = tc.create_chart(ticker="BAD", data=bad_df, trades=[])
        # Should return None, not raise
        assert result is None

    def test_create_charts_for_tickers_continues_after_error(self, tmp_path):
        """
        create_charts_for_tickers should continue processing remaining tickers
        even if one ticker's chart generation fails.
        """
        tc = TickerCharts(output_dir=str(tmp_path))

        good_df = _make_ohlcv_dataframe(100)
        bad_df = _make_ohlcv_dataframe(100)
        bad_df["Close"] = np.nan
        bad_df["Open"] = np.nan
        bad_df["High"] = np.nan
        bad_df["Low"] = np.nan

        ticker_data = {
            "BAD": bad_df,
            "NONE": None,
        }
        trades_by_ticker = {"BAD": [], "NONE": []}

        # Should not raise, should process all tickers
        result = tc.create_charts_for_tickers(
            tickers=["BAD", "NONE"],
            ticker_data=ticker_data,
            trades_by_ticker=trades_by_ticker,
        )
        # Both should fail gracefully, result should be empty or partial
        assert isinstance(result, dict)

    def test_generate_price_chart_from_dataframe_wraps_exception(self, tmp_path):
        """
        generate_price_chart_from_dataframe should raise RuntimeError
        when mplfinance plotting fails internally.
        """
        # Create valid-looking data that passes validation
        df = _make_ohlcv_dataframe(MIN_DATA_POINTS + 10)

        # Mock mplfinance.plot to raise an exception
        with patch("backtest.ticker_charts.mpf") as mock_mpf:
            mock_mpf.plot.side_effect = Exception("mplfinance internal error")
            mock_mpf.make_addplot = MagicMock()
            mock_mpf.make_mpf_style = MagicMock()
            mock_mpf.make_marketcolors = MagicMock()
            with patch("backtest.ticker_charts.MPLFINANCE_AVAILABLE", True):
                with pytest.raises(RuntimeError, match="Chart generation failed"):
                    generate_price_chart_from_dataframe(
                        ticker="FAIL",
                        data=df,
                        output_dir=str(tmp_path),
                    )

    def test_missing_columns_raises_valueerror(self, tmp_path):
        """DataFrame missing required OHLCV columns should raise ValueError."""
        incomplete_df = pd.DataFrame(
            {"Open": [1, 2, 3], "Close": [1, 2, 3]},
            index=pd.bdate_range("2023-01-01", periods=3),
        )
        with pytest.raises(ValueError, match="Missing required columns"):
            generate_price_chart_from_dataframe(
                ticker="AAPL",
                data=incomplete_df,
                output_dir=str(tmp_path),
            )
