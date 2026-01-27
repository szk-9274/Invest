"""
Unit tests for technical indicators
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from analysis.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_52w_high_low,
    calculate_atr,
    calculate_rs_line,
    is_rs_new_high,
    calculate_bollinger_bands,
    calculate_volume_ma,
    calculate_all_indicators
)


def create_sample_data(days: int = 300) -> pd.DataFrame:
    """Create sample stock data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    np.random.seed(42)

    # Generate realistic price data
    base_price = 100
    returns = np.random.normal(0.0005, 0.02, days)
    prices = base_price * np.exp(np.cumsum(returns))

    data = pd.DataFrame({
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        'high': prices * (1 + np.random.uniform(0, 0.02, days)),
        'low': prices * (1 - np.random.uniform(0, 0.02, days)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, days)
    }, index=dates)

    return data


class TestSMA:
    """Tests for SMA calculation"""

    def test_calculate_sma_single_period(self):
        """Test SMA calculation with single period"""
        data = pd.DataFrame({
            'close': [100, 102, 104, 106, 108, 110]
        })

        result = calculate_sma(data, [3])

        assert 'sma_3' in result.columns
        expected = (106 + 108 + 110) / 3
        assert abs(result['sma_3'].iloc[-1] - expected) < 0.01

    def test_calculate_sma_multiple_periods(self):
        """Test SMA calculation with multiple periods"""
        data = create_sample_data(200)

        result = calculate_sma(data, [50, 150, 200])

        assert 'sma_50' in result.columns
        assert 'sma_150' in result.columns
        assert 'sma_200' in result.columns

    def test_calculate_sma_nan_at_start(self):
        """Test that SMA has NaN values at the start"""
        data = pd.DataFrame({
            'close': list(range(10))
        })

        result = calculate_sma(data, [5])

        # First 4 values should be NaN (need 5 data points for 5-period SMA)
        assert pd.isna(result['sma_5'].iloc[:4]).all()
        assert not pd.isna(result['sma_5'].iloc[4])


class TestEMA:
    """Tests for EMA calculation"""

    def test_calculate_ema(self):
        """Test EMA calculation"""
        data = pd.DataFrame({
            'close': [100, 102, 104, 106, 108, 110]
        })

        result = calculate_ema(data, 3)

        assert len(result) == 6
        assert not pd.isna(result.iloc[-1])


class Test52WeekHighLow:
    """Tests for 52-week high/low calculation"""

    def test_calculate_52w_high_low(self):
        """Test 52-week high/low calculation"""
        data = create_sample_data(300)

        high_52w, low_52w = calculate_52w_high_low(data)

        # Should be within reasonable range
        assert high_52w > low_52w
        assert high_52w == data['high'].tail(252).max()
        assert low_52w == data['low'].tail(252).min()

    def test_calculate_52w_with_short_data(self):
        """Test with less than 252 days of data"""
        data = create_sample_data(100)

        high_52w, low_52w = calculate_52w_high_low(data)

        # Should use all available data
        assert high_52w == data['high'].max()
        assert low_52w == data['low'].min()


class TestATR:
    """Tests for ATR calculation"""

    def test_calculate_atr(self):
        """Test ATR calculation"""
        data = create_sample_data(100)

        atr = calculate_atr(data, 14)

        assert len(atr) == len(data)
        # ATR should be positive
        assert atr.dropna().iloc[-1] > 0


class TestRSLine:
    """Tests for RS Line calculation"""

    def test_calculate_rs_line(self):
        """Test RS Line calculation"""
        stock_data = create_sample_data(100)
        benchmark_data = create_sample_data(100)

        rs_line = calculate_rs_line(stock_data, benchmark_data)

        assert len(rs_line) > 0
        # RS line should be positive
        assert (rs_line > 0).all()

    def test_is_rs_new_high(self):
        """Test RS new high detection"""
        # Create RS line that ends at new high
        rs_values = list(range(1, 253))  # Steadily increasing
        rs_line = pd.Series(rs_values)

        result = is_rs_new_high(rs_line)

        assert result == True

    def test_is_rs_not_new_high(self):
        """Test RS not at new high"""
        # Create RS line that ends below previous high
        rs_values = list(range(1, 200)) + list(range(200, 150, -1))
        rs_line = pd.Series(rs_values)

        result = is_rs_new_high(rs_line)

        assert result is False


class TestBollingerBands:
    """Tests for Bollinger Bands calculation"""

    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        data = create_sample_data(100)

        bb = calculate_bollinger_bands(data, period=20, std_dev=2.0)

        assert 'middle' in bb
        assert 'upper' in bb
        assert 'lower' in bb

        # Upper should be above middle, middle above lower
        last_idx = -1
        assert bb['upper'].iloc[last_idx] > bb['middle'].iloc[last_idx]
        assert bb['middle'].iloc[last_idx] > bb['lower'].iloc[last_idx]


class TestVolumeMA:
    """Tests for Volume MA calculation"""

    def test_calculate_volume_ma(self):
        """Test Volume MA calculation"""
        data = create_sample_data(100)

        vol_ma = calculate_volume_ma(data, 10)

        assert len(vol_ma) == len(data)
        assert not pd.isna(vol_ma.iloc[-1])


class TestAllIndicators:
    """Tests for all indicators calculation"""

    def test_calculate_all_indicators(self):
        """Test all indicators calculation"""
        data = create_sample_data(300)
        benchmark = create_sample_data(300)

        result = calculate_all_indicators(data, benchmark)

        # Check all expected columns exist
        expected_cols = [
            'sma_50', 'sma_150', 'sma_200',
            'ema_21', 'atr_14', 'rs_line',
            'bb_middle', 'bb_upper', 'bb_lower',
            'volume_ma_10', 'volume_ma_50'
        ]

        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"
