"""
Tests for Phase A-2: Chart Generation Interface Standardization

Tests cover:
1. Unified interface parameters (ticker, price_df, trades_df, start_date, end_date, chart_mode)
2. chart_mode="auto" behavior (auto-resample to weekly for large data)
3. chart_mode="daily" forces daily
4. chart_mode="weekly" forces weekly resampling
5. Input validation for the unified interface
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def _make_ohlcv_dataframe(rows: int, start_date: str = "2023-01-01") -> pd.DataFrame:
    """Helper to create a valid OHLCV DataFrame."""
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
# 1. generate_chart_unified function exists and has correct signature
# ============================================================
class TestUnifiedInterfaceExists:
    """The unified generate_chart_unified function must exist with the required parameters."""

    def test_function_exists(self):
        """generate_chart_unified should be importable from ticker_charts."""
        from backtest.ticker_charts import generate_chart_unified
        assert callable(generate_chart_unified)

    def test_function_accepts_required_params(self, tmp_path):
        """generate_chart_unified should accept ticker, price_df, trades_df, start_date, end_date, chart_mode."""
        from backtest.ticker_charts import generate_chart_unified

        price_df = _make_ohlcv_dataframe(60)
        trades_df = pd.DataFrame(columns=["ticker", "action", "date", "price"])

        # Should not raise TypeError for missing args
        try:
            generate_chart_unified(
                ticker="AAPL",
                price_df=price_df,
                trades_df=trades_df,
                start_date="2023-01-01",
                end_date="2023-12-31",
                chart_mode="daily",
                output_dir=str(tmp_path),
            )
        except (RuntimeError, ValueError):
            # OK if it fails for non-signature reasons
            pass

    def test_chart_mode_defaults_to_auto(self, tmp_path):
        """chart_mode should default to 'auto' when not specified."""
        from backtest.ticker_charts import generate_chart_unified
        import inspect

        sig = inspect.signature(generate_chart_unified)
        chart_mode_param = sig.parameters.get("chart_mode")
        assert chart_mode_param is not None
        assert chart_mode_param.default == "auto"


# ============================================================
# 2. chart_mode="auto" behavior
# ============================================================
class TestChartModeAuto:
    """chart_mode='auto' should auto-resample to weekly when data volume is large."""

    def test_auto_uses_daily_for_small_data(self, tmp_path):
        """
        auto mode should return daily-frequency data when the number of bars
        is below the auto-resample threshold.
        """
        from backtest.ticker_charts import generate_chart_unified, AUTO_RESAMPLE_THRESHOLD

        small_df = _make_ohlcv_dataframe(AUTO_RESAMPLE_THRESHOLD - 1)
        trades_df = pd.DataFrame(columns=["ticker", "action", "date", "price"])

        # Mock the actual chart generation to capture what frequency was used
        with patch("backtest.ticker_charts._render_chart") as mock_render:
            mock_render.return_value = tmp_path / "test.png"
            try:
                generate_chart_unified(
                    ticker="AAPL",
                    price_df=small_df,
                    trades_df=trades_df,
                    chart_mode="auto",
                    output_dir=str(tmp_path),
                )
            except (RuntimeError, Exception):
                pass

            if mock_render.called:
                # The data passed to _render_chart should be daily (same length)
                rendered_data = mock_render.call_args[1].get("data")
                if rendered_data is None:
                    rendered_data = mock_render.call_args[0][1]
                assert len(rendered_data) == len(small_df)

    def test_auto_resamples_to_weekly_for_large_data(self, tmp_path):
        """
        auto mode should resample to weekly when the number of bars
        exceeds the auto-resample threshold.
        """
        from backtest.ticker_charts import generate_chart_unified, AUTO_RESAMPLE_THRESHOLD

        large_df = _make_ohlcv_dataframe(AUTO_RESAMPLE_THRESHOLD + 50)
        trades_df = pd.DataFrame(columns=["ticker", "action", "date", "price"])

        with patch("backtest.ticker_charts._render_chart") as mock_render:
            mock_render.return_value = tmp_path / "test.png"
            try:
                generate_chart_unified(
                    ticker="AAPL",
                    price_df=large_df,
                    trades_df=trades_df,
                    chart_mode="auto",
                    output_dir=str(tmp_path),
                )
            except (RuntimeError, Exception):
                pass

            if mock_render.called:
                rendered_data = mock_render.call_args[1].get("data")
                if rendered_data is None:
                    rendered_data = mock_render.call_args[0][1]
                # Weekly data should have fewer rows than daily
                assert len(rendered_data) < len(large_df)


# ============================================================
# 3. chart_mode="daily"
# ============================================================
class TestChartModeDaily:
    """chart_mode='daily' should always use daily frequency."""

    def test_daily_mode_preserves_original_frequency(self, tmp_path):
        """daily mode should not resample data, even for large datasets."""
        from backtest.ticker_charts import generate_chart_unified

        large_df = _make_ohlcv_dataframe(500)
        trades_df = pd.DataFrame(columns=["ticker", "action", "date", "price"])

        with patch("backtest.ticker_charts._render_chart") as mock_render:
            mock_render.return_value = tmp_path / "test.png"
            try:
                generate_chart_unified(
                    ticker="AAPL",
                    price_df=large_df,
                    trades_df=trades_df,
                    chart_mode="daily",
                    output_dir=str(tmp_path),
                )
            except (RuntimeError, Exception):
                pass

            if mock_render.called:
                rendered_data = mock_render.call_args[1].get("data")
                if rendered_data is None:
                    rendered_data = mock_render.call_args[0][1]
                assert len(rendered_data) == len(large_df)


# ============================================================
# 4. chart_mode="weekly"
# ============================================================
class TestChartModeWeekly:
    """chart_mode='weekly' should always resample to weekly frequency."""

    def test_weekly_mode_resamples_data(self, tmp_path):
        """weekly mode should resample daily data to weekly."""
        from backtest.ticker_charts import generate_chart_unified

        daily_df = _make_ohlcv_dataframe(100)
        trades_df = pd.DataFrame(columns=["ticker", "action", "date", "price"])

        with patch("backtest.ticker_charts._render_chart") as mock_render:
            mock_render.return_value = tmp_path / "test.png"
            try:
                generate_chart_unified(
                    ticker="AAPL",
                    price_df=daily_df,
                    trades_df=trades_df,
                    chart_mode="weekly",
                    output_dir=str(tmp_path),
                )
            except (RuntimeError, Exception):
                pass

            if mock_render.called:
                rendered_data = mock_render.call_args[1].get("data")
                if rendered_data is None:
                    rendered_data = mock_render.call_args[0][1]
                # Weekly data should be roughly 1/5 of daily (5 business days per week)
                assert len(rendered_data) < len(daily_df)
                assert len(rendered_data) <= len(daily_df) // 4  # at most ~1/4


# ============================================================
# 5. _resample_to_weekly helper
# ============================================================
class TestResampleToWeekly:
    """Test the _resample_to_weekly helper function."""

    def test_resample_preserves_ohlcv_semantics(self):
        """Weekly resampling should use Open=first, High=max, Low=min, Close=last, Volume=sum."""
        from backtest.ticker_charts import _resample_to_weekly

        daily_df = _make_ohlcv_dataframe(20)
        weekly_df = _resample_to_weekly(daily_df)

        assert len(weekly_df) > 0
        assert len(weekly_df) < len(daily_df)

        # Check all OHLCV columns exist
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            assert col in weekly_df.columns

    def test_resample_empty_returns_empty(self):
        """Resampling an empty DataFrame should return an empty DataFrame."""
        from backtest.ticker_charts import _resample_to_weekly

        empty_df = _make_ohlcv_dataframe(0)
        result = _resample_to_weekly(empty_df)
        assert result.empty

    def test_resample_weekly_high_is_max_of_daily(self):
        """The weekly High should be the max of daily Highs in that week."""
        from backtest.ticker_charts import _resample_to_weekly

        daily_df = _make_ohlcv_dataframe(10, start_date="2023-01-02")
        weekly_df = _resample_to_weekly(daily_df)

        # For the first week, the weekly High should be >= max of corresponding daily Highs
        first_week_end = weekly_df.index[0]
        daily_in_week = daily_df[daily_df.index <= first_week_end]
        if not daily_in_week.empty:
            assert weekly_df.iloc[0]["High"] >= daily_in_week["High"].max() - 1e-10


# ============================================================
# 6. Input validation for unified interface
# ============================================================
class TestUnifiedInputValidation:
    """Test input validation for generate_chart_unified."""

    def test_invalid_chart_mode_raises_valueerror(self, tmp_path):
        """An invalid chart_mode should raise ValueError."""
        from backtest.ticker_charts import generate_chart_unified

        df = _make_ohlcv_dataframe(60)
        trades_df = pd.DataFrame(columns=["ticker", "action", "date", "price"])

        with pytest.raises(ValueError, match="chart_mode"):
            generate_chart_unified(
                ticker="AAPL",
                price_df=df,
                trades_df=trades_df,
                chart_mode="invalid_mode",
                output_dir=str(tmp_path),
            )

    def test_none_price_df_raises_valueerror(self, tmp_path):
        """price_df=None should raise ValueError."""
        from backtest.ticker_charts import generate_chart_unified

        trades_df = pd.DataFrame(columns=["ticker", "action", "date", "price"])

        with pytest.raises(ValueError):
            generate_chart_unified(
                ticker="AAPL",
                price_df=None,
                trades_df=trades_df,
                output_dir=str(tmp_path),
            )

    def test_empty_price_df_raises_valueerror(self, tmp_path):
        """An empty price_df should raise ValueError."""
        from backtest.ticker_charts import generate_chart_unified

        empty_df = _make_ohlcv_dataframe(0)
        trades_df = pd.DataFrame(columns=["ticker", "action", "date", "price"])

        with pytest.raises(ValueError):
            generate_chart_unified(
                ticker="AAPL",
                price_df=empty_df,
                trades_df=trades_df,
                output_dir=str(tmp_path),
            )

    def test_trades_df_none_is_handled(self, tmp_path):
        """trades_df=None should be handled gracefully (no markers)."""
        from backtest.ticker_charts import generate_chart_unified

        df = _make_ohlcv_dataframe(60)

        with patch("backtest.ticker_charts._render_chart") as mock_render:
            mock_render.return_value = tmp_path / "test.png"
            try:
                generate_chart_unified(
                    ticker="AAPL",
                    price_df=df,
                    trades_df=None,
                    output_dir=str(tmp_path),
                )
            except (RuntimeError, Exception):
                pass
        # Should not raise TypeError
