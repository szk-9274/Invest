"""
Unit tests for Stage Detector
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from analysis.stage_detector import StageDetector, is_stage2
from analysis.indicators import calculate_all_indicators


def create_stage2_data(days: int = 300) -> pd.DataFrame:
    """Create sample data that meets Stage 2 conditions"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # Create uptrending price data
    base_price = 100
    trend = np.linspace(0, 0.5, days)  # Strong uptrend
    noise = np.random.normal(0, 0.01, days)
    prices = base_price * np.exp(trend + noise)

    data = pd.DataFrame({
        'open': prices * 0.998,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(500000, 2000000, days)
    }, index=dates)

    return data


def create_stage4_data(days: int = 300) -> pd.DataFrame:
    """Create sample data that indicates Stage 4 (declining)"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # Create downtrending price data
    base_price = 200
    trend = np.linspace(0, -0.4, days)  # Downtrend
    noise = np.random.normal(0, 0.01, days)
    prices = base_price * np.exp(trend + noise)

    data = pd.DataFrame({
        'open': prices * 1.002,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(500000, 2000000, days)
    }, index=dates)

    return data


def get_default_params() -> dict:
    """Get default stage detection parameters"""
    return {
        'sma_periods': [50, 150, 200],
        'min_price_above_52w_low': 1.30,
        'max_distance_from_52w_high': 0.75,
        'min_slope_200_days': 20,
        'rs_min_rating': 70,
        'rs_new_high_required': True,
        'min_volume': 500000
    }


class TestStageDetector:
    """Tests for StageDetector class"""

    def test_initialization(self):
        """Test detector initialization"""
        params = get_default_params()
        detector = StageDetector(params)

        assert detector.params == params

    def test_detect_stage2_conditions(self):
        """Test Stage 2 condition checking"""
        params = get_default_params()
        detector = StageDetector(params)

        # Create Stage 2 data
        data = create_stage2_data()
        benchmark = create_stage2_data()

        # Calculate indicators
        data = calculate_all_indicators(data, benchmark)

        # Check conditions
        conditions = detector.check_stage2_conditions(data, data['rs_line'])

        # Should have all condition keys
        assert 'price_above_sma50' in conditions
        assert 'sma50_above_sma150' in conditions
        assert 'sma150_above_sma200' in conditions
        assert 'ma200_uptrend' in conditions
        assert 'above_52w_low' in conditions
        assert 'near_52w_high' in conditions

    def test_detect_stage2(self):
        """Test Stage 2 detection"""
        params = get_default_params()
        detector = StageDetector(params)

        # Create Stage 2 data
        data = create_stage2_data()
        benchmark = create_stage2_data()
        data = calculate_all_indicators(data, benchmark)

        result = detector.detect_stage(data, data['rs_line'])

        assert 'stage' in result
        assert 'meets_criteria' in result
        assert 'details' in result
        assert result['stage'] in [1, 2, 3, 4]

    def test_detect_stage4(self):
        """Test Stage 4 detection"""
        params = get_default_params()
        detector = StageDetector(params)

        # Create Stage 4 data
        data = create_stage4_data()
        benchmark = create_stage2_data()
        data = calculate_all_indicators(data, benchmark)

        result = detector.detect_stage(data, data['rs_line'])

        # Stage 4 should be detected for declining stock
        assert result['stage'] in [1, 3, 4]  # Not Stage 2

    def test_is_stage2_function(self):
        """Test is_stage2 helper function"""
        params = get_default_params()

        data = create_stage2_data()
        benchmark = create_stage2_data()
        data = calculate_all_indicators(data, benchmark)

        # Function should return boolean
        result = is_stage2(data, data['rs_line'], params)

        assert isinstance(result, bool)

    def test_ma200_slope_calculation(self):
        """Test 200-day MA slope calculation"""
        params = get_default_params()
        detector = StageDetector(params)

        # Create uptrending data
        data = create_stage2_data()
        benchmark = create_stage2_data()
        data = calculate_all_indicators(data, benchmark)

        slope = detector._calculate_ma200_slope(data)

        # Should be positive for uptrending stock
        assert slope > 0

    def test_52w_high_low_calculation(self):
        """Test 52-week high/low calculation"""
        params = get_default_params()
        detector = StageDetector(params)

        data = create_stage2_data()

        high_52w, low_52w = detector._get_52w_high_low(data)

        assert high_52w > low_52w
        assert high_52w == data['high'].tail(252).max()
        assert low_52w == data['low'].tail(252).min()

    def test_insufficient_data(self):
        """Test handling of insufficient data"""
        params = get_default_params()
        detector = StageDetector(params)

        # Create very short data
        dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
        data = pd.DataFrame({
            'open': [100] * 50,
            'high': [101] * 50,
            'low': [99] * 50,
            'close': [100] * 50,
            'volume': [1000000] * 50
        }, index=dates)

        benchmark = data.copy()
        data = calculate_all_indicators(data, benchmark)

        conditions = detector.check_stage2_conditions(data, data['rs_line'])

        # All conditions should be False due to insufficient data
        assert all(v is False for v in conditions.values())


class TestStage2Conditions:
    """Detailed tests for individual Stage 2 conditions"""

    def test_price_above_ma_condition(self):
        """Test price above MA condition"""
        params = get_default_params()
        detector = StageDetector(params)

        data = create_stage2_data()
        benchmark = create_stage2_data()
        data = calculate_all_indicators(data, benchmark)

        conditions = detector.check_stage2_conditions(data, data['rs_line'])

        # Check the specific condition logic
        latest = data.iloc[-1]
        expected = latest['close'] > latest['sma_50']
        assert conditions['price_above_sma50'] == expected

    def test_volume_condition(self):
        """Test volume condition"""
        params = get_default_params()
        detector = StageDetector(params)

        data = create_stage2_data()
        benchmark = create_stage2_data()
        data = calculate_all_indicators(data, benchmark)

        conditions = detector.check_stage2_conditions(data, data['rs_line'])

        latest = data.iloc[-1]
        expected = latest['volume_ma_50'] >= params['min_volume']
        assert conditions['sufficient_volume'] == expected
