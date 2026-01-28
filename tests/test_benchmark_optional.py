"""
Unit tests for benchmark-optional behavior.
Verifies that Stage 2 detection, indicators, and backtest engine
work correctly both with and without benchmark data.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from analysis.indicators import calculate_all_indicators
from analysis.stage_detector import StageDetector, is_stage2


_FIXED_END_DATE = '2025-01-01'


def create_uptrending_data(days: int = 300) -> pd.DataFrame:
    """Create sample uptrending stock data"""
    dates = pd.date_range(end=_FIXED_END_DATE, periods=days, freq='D')
    np.random.seed(42)

    base_price = 100
    trend = np.linspace(0, 0.5, days)
    noise = np.random.normal(0, 0.01, days)
    prices = base_price * np.exp(trend + noise)

    return pd.DataFrame({
        'open': prices * 0.998,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(500000, 2000000, days)
    }, index=dates)


def create_benchmark_data(days: int = 300) -> pd.DataFrame:
    """Create sample benchmark data"""
    dates = pd.date_range(end=_FIXED_END_DATE, periods=days, freq='D')
    np.random.seed(43)

    base_price = 450
    trend = np.linspace(0, 0.3, days)
    noise = np.random.normal(0, 0.01, days)
    prices = base_price * np.exp(trend + noise)

    return pd.DataFrame({
        'open': prices * 0.998,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(50000000, 100000000, days)
    }, index=dates)


def get_stage_params() -> dict:
    return {
        'sma_periods': [50, 150, 200],
        'min_price_above_52w_low': 1.30,
        'max_distance_from_52w_high': 0.75,
        'min_slope_200_days': 20,
        'rs_min_rating': 70,
        'rs_new_high_required': True,
        'min_volume': 500000
    }


class TestIndicatorsWithoutBenchmark:
    """Test that indicators work without benchmark data."""

    def test_all_indicators_no_benchmark(self):
        """calculate_all_indicators should work when benchmark_data=None."""
        data = create_uptrending_data(300)
        result = calculate_all_indicators(data, benchmark_data=None)

        # All columns should exist
        assert 'sma_50' in result.columns
        assert 'sma_150' in result.columns
        assert 'sma_200' in result.columns
        assert 'ema_21' in result.columns
        assert 'atr_14' in result.columns
        assert 'rs_line' in result.columns
        assert 'bb_middle' in result.columns
        assert 'volume_ma_50' in result.columns

    def test_rs_line_empty_without_benchmark(self):
        """RS line should be empty/NaN when no benchmark provided."""
        data = create_uptrending_data(300)
        result = calculate_all_indicators(data, benchmark_data=None)

        # rs_line should exist but be empty
        assert 'rs_line' in result.columns
        assert result['rs_line'].isna().all() or len(result['rs_line'].dropna()) == 0

    def test_all_indicators_with_benchmark(self):
        """calculate_all_indicators should still work with benchmark."""
        data = create_uptrending_data(300)
        benchmark = create_benchmark_data(300)
        result = calculate_all_indicators(data, benchmark)

        assert 'rs_line' in result.columns
        assert len(result['rs_line'].dropna()) > 0


class TestStageDetectorWithoutBenchmark:
    """Test StageDetector with use_benchmark=False."""

    def test_detect_stage_no_benchmark(self):
        """Stage detection should work without benchmark."""
        params = get_stage_params()
        detector = StageDetector(params)

        data = create_uptrending_data(300)
        data = calculate_all_indicators(data, benchmark_data=None)

        result = detector.detect_stage(data, rs_line=None, use_benchmark=False)

        assert 'stage' in result
        assert 'meets_criteria' in result
        assert 'details' in result
        assert result['stage'] in [1, 2, 3, 4]

    def test_rs_new_high_auto_true_no_benchmark(self):
        """RS new high should be True when benchmark disabled."""
        params = get_stage_params()
        detector = StageDetector(params)

        data = create_uptrending_data(300)
        data = calculate_all_indicators(data, benchmark_data=None)

        conditions = detector.check_stage2_conditions(
            data, rs_line=None, use_benchmark=False
        )

        assert conditions['rs_new_high'] is True

    def test_rs_new_high_checked_with_benchmark(self):
        """RS new high should be actually checked when benchmark is enabled."""
        params = get_stage_params()
        detector = StageDetector(params)

        data = create_uptrending_data(300)
        benchmark = create_benchmark_data(300)
        data = calculate_all_indicators(data, benchmark)

        conditions = detector.check_stage2_conditions(
            data, rs_line=data['rs_line'], use_benchmark=True
        )

        # rs_new_high should be a boolean (True or False)
        assert isinstance(conditions['rs_new_high'], (bool, np.bool_))

    def test_non_benchmark_conditions_same(self):
        """Non-benchmark conditions should be identical regardless of benchmark flag."""
        params = get_stage_params()
        detector = StageDetector(params)

        data = create_uptrending_data(300)
        benchmark = create_benchmark_data(300)
        data_with_bench = calculate_all_indicators(data.copy(), benchmark)
        data_no_bench = calculate_all_indicators(data.copy(), benchmark_data=None)

        cond_with = detector.check_stage2_conditions(
            data_with_bench, rs_line=data_with_bench['rs_line'], use_benchmark=True
        )
        cond_without = detector.check_stage2_conditions(
            data_no_bench, rs_line=None, use_benchmark=False
        )

        # All conditions except rs_new_high should match
        for key in cond_with:
            if key != 'rs_new_high':
                assert cond_with[key] == cond_without[key], (
                    f"Condition '{key}' differs: with_bench={cond_with[key]}, "
                    f"without_bench={cond_without[key]}"
                )


class TestIsStage2Helper:
    """Test the is_stage2 helper function."""

    def test_is_stage2_no_benchmark(self):
        """is_stage2 should work with use_benchmark=False."""
        params = get_stage_params()
        data = create_uptrending_data(300)
        data = calculate_all_indicators(data, benchmark_data=None)

        result = is_stage2(data, rs_line=None, params=params, use_benchmark=False)
        assert isinstance(result, bool)

    def test_is_stage2_with_benchmark(self):
        """is_stage2 should work with use_benchmark=True."""
        params = get_stage_params()
        data = create_uptrending_data(300)
        benchmark = create_benchmark_data(300)
        data = calculate_all_indicators(data, benchmark)

        result = is_stage2(data, rs_line=data['rs_line'], params=params, use_benchmark=True)
        assert isinstance(result, bool)


class TestInsufficientData:
    """Test handling of insufficient data."""

    def test_short_data_no_benchmark(self):
        """Short data should return all-False conditions."""
        params = get_stage_params()
        detector = StageDetector(params)

        dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
        data = pd.DataFrame({
            'open': [100] * 50,
            'high': [101] * 50,
            'low': [99] * 50,
            'close': [100] * 50,
            'volume': [1000000] * 50
        }, index=dates)

        data = calculate_all_indicators(data, benchmark_data=None)
        conditions = detector.check_stage2_conditions(
            data, rs_line=None, use_benchmark=False
        )

        assert all(v is False for v in conditions.values())
