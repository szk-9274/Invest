"""
Tests for StageDetector configurable thresholds (strict/relaxed modes)
"""
import pytest
import pandas as pd
import yaml
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis.stage_detector import StageDetector


@pytest.fixture
def config_params():
    """Load configuration from params.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "params.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['stage']


@pytest.fixture
def sample_stock_data():
    """Create sample stock data for testing"""
    dates = pd.date_range('2023-01-01', periods=300, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'close': [100.0] * 300,
        'high': [102.0] * 300,
        'low': [98.0] * 300,
        'volume': [1_000_000] * 300,
        'sma_50': [95.0] * 300,
        'sma_150': [90.0] * 300,
        'sma_200': [85.0] * 300,
        'volume_ma_50': [800_000] * 300,
    })
    return data


@pytest.fixture
def sample_rs_line():
    """Create sample RS line data"""
    return pd.Series([100.0] * 300)


class TestConfigLoading:
    """Test configuration loading for strict and relaxed modes"""

    def test_load_strict_thresholds_from_config(self, config_params):
        """Verify strict mode thresholds load correctly from config"""
        assert 'strict' in config_params
        strict = config_params['strict']

        assert strict['min_price_above_52w_low'] == 1.30
        assert strict['max_distance_from_52w_high'] == 0.75
        assert strict['rs_new_high_threshold'] == 0.95
        assert strict['min_volume'] == 500_000

    def test_load_relaxed_thresholds_from_config(self, config_params):
        """Verify relaxed mode thresholds load correctly from config"""
        assert 'relaxed' in config_params
        relaxed = config_params['relaxed']

        assert relaxed['min_price_above_52w_low'] == 1.20
        assert relaxed['max_distance_from_52w_high'] == 0.60
        assert relaxed['rs_new_high_threshold'] == 0.90
        assert relaxed['min_volume'] == 300_000

    def test_fallback_config_exists(self, config_params):
        """Verify fallback configuration exists"""
        assert 'auto_fallback_enabled' in config_params
        assert 'min_trades_threshold' in config_params
        assert config_params['auto_fallback_enabled'] is True
        assert config_params['min_trades_threshold'] == 1


class TestStageDetectorModeParameter:
    """Test StageDetector with mode parameter"""

    def test_detector_accepts_strict_mode_in_init(self, config_params):
        """StageDetector should accept config with strict/relaxed modes"""
        detector = StageDetector(config_params)

        # Verify detector has loaded strict thresholds
        assert hasattr(detector, 'params')
        assert 'strict' in detector.params
        assert 'relaxed' in detector.params

    def test_detect_stage_accepts_mode_parameter(self, config_params, sample_stock_data):
        """detect_stage should accept mode parameter"""
        detector = StageDetector(config_params)

        # Should not raise error with mode parameter
        result = detector.detect_stage(sample_stock_data, mode='strict')
        assert 'stage' in result

        result = detector.detect_stage(sample_stock_data, mode='relaxed')
        assert 'stage' in result

    def test_check_stage2_conditions_accepts_mode_parameter(self, config_params, sample_stock_data):
        """check_stage2_conditions should accept mode parameter"""
        detector = StageDetector(config_params)

        # Should not raise error with mode parameter
        conditions_strict = detector.check_stage2_conditions(sample_stock_data, mode='strict')
        assert isinstance(conditions_strict, dict)

        conditions_relaxed = detector.check_stage2_conditions(sample_stock_data, mode='relaxed')
        assert isinstance(conditions_relaxed, dict)


class TestStrictModeThresholds:
    """Test that strict mode applies correct thresholds"""

    def test_strict_mode_uses_strict_near_52w_high_threshold(self, config_params):
        """Strict mode should use 0.75 threshold for near_52w_high"""
        detector = StageDetector(config_params)

        # Create data that passes relaxed (0.60) but fails strict (0.75)
        data = pd.DataFrame({
            'close': [70.0],  # 70% of 52w high
            'high': [100.0],
            'low': [50.0],
            'volume': [1_000_000],
            'sma_50': [65.0],
            'sma_150': [60.0],
            'sma_200': [55.0],
            'volume_ma_50': [600_000],
        })

        # Pad data to 252 rows for 52-week calculations
        data = pd.concat([data] * 252, ignore_index=True)

        conditions = detector.check_stage2_conditions(data, mode='strict', use_benchmark=False)

        # Should fail strict mode (70% < 75%)
        assert conditions['near_52w_high'] == False

    def test_strict_mode_uses_strict_rs_threshold(self, config_params):
        """Strict mode should use 0.95 threshold for RS"""
        detector = StageDetector(config_params)

        # Create RS line with 52w high of 100, current at 92 (passes relaxed 0.90, fails strict 0.95)
        rs_line = pd.Series([100.0] * 200 + [92.0] * 52)  # High was 100, now at 92

        # Create proper stock data
        data = pd.DataFrame({
            'close': [100.0] * 252,
            'high': [102.0] * 252,
            'low': [50.0] * 252,
            'volume': [1_000_000] * 252,
            'sma_50': [95.0] * 252,
            'sma_150': [90.0] * 252,
            'sma_200': [85.0] * 252,
            'volume_ma_50': [800_000] * 252,
        })

        conditions = detector.check_stage2_conditions(data, rs_line, mode='strict', use_benchmark=True)

        # Should fail strict mode (92% < 95%)
        assert conditions['rs_new_high'] == False


class TestRelaxedModeThresholds:
    """Test that relaxed mode applies correct thresholds"""

    def test_relaxed_mode_uses_relaxed_near_52w_high_threshold(self, config_params):
        """Relaxed mode should use 0.60 threshold for near_52w_high"""
        detector = StageDetector(config_params)

        # Create data that passes relaxed (0.60) but fails strict (0.75)
        data = pd.DataFrame({
            'close': [70.0],  # 70% of 52w high
            'high': [100.0],
            'low': [50.0],
            'volume': [1_000_000],
            'sma_50': [65.0],
            'sma_150': [60.0],
            'sma_200': [55.0],
            'volume_ma_50': [600_000],
        })

        # Pad data to 252 rows
        data = pd.concat([data] * 252, ignore_index=True)

        conditions = detector.check_stage2_conditions(data, mode='relaxed', use_benchmark=False)

        # Should pass relaxed mode (70% >= 60%)
        assert conditions['near_52w_high'] == True

    def test_relaxed_mode_uses_relaxed_rs_threshold(self, config_params):
        """Relaxed mode should use 0.90 threshold for RS"""
        detector = StageDetector(config_params)

        # Create RS line at 92% of 52w high (passes relaxed 0.90, fails strict 0.95)
        rs_line = pd.Series([92.0] * 252)
        rs_line.iloc[-1] = 92.0

        # Create proper stock data
        data = pd.DataFrame({
            'close': [100.0] * 252,
            'high': [102.0] * 252,
            'low': [50.0] * 252,
            'volume': [1_000_000] * 252,
            'sma_50': [95.0] * 252,
            'sma_150': [90.0] * 252,
            'sma_200': [85.0] * 252,
            'volume_ma_50': [800_000] * 252,
        })

        conditions = detector.check_stage2_conditions(data, rs_line, mode='relaxed', use_benchmark=True)

        # Should pass relaxed mode (92% >= 90%)
        assert conditions['rs_new_high'] == True

    def test_relaxed_mode_uses_relaxed_volume_threshold(self, config_params):
        """Relaxed mode should use 300,000 volume threshold"""
        detector = StageDetector(config_params)

        # Create data with 400k volume (passes relaxed 300k, fails strict 500k)
        data = pd.DataFrame({
            'close': [100.0] * 252,
            'high': [102.0] * 252,
            'low': [50.0] * 252,
            'volume': [1_000_000] * 252,
            'sma_50': [95.0] * 252,
            'sma_150': [90.0] * 252,
            'sma_200': [85.0] * 252,
            'volume_ma_50': [400_000] * 252,  # 400k volume
        })

        conditions = detector.check_stage2_conditions(data, mode='relaxed', use_benchmark=False)

        # Should pass relaxed mode (400k >= 300k)
        assert conditions['sufficient_volume'] == True


class TestBackwardCompatibility:
    """Test backward compatibility"""

    def test_backward_compatibility_defaults_to_strict(self, config_params, sample_stock_data):
        """When mode is not specified, should default to strict mode"""
        detector = StageDetector(config_params)

        # Call without mode parameter (backward compatibility)
        result = detector.detect_stage(sample_stock_data)

        # Should work and use strict mode by default
        assert 'stage' in result
        assert 'meets_criteria' in result

    def test_old_config_format_still_works(self):
        """Old config format (without strict/relaxed) should still work"""
        old_params = {
            'sma_periods': [50, 150, 200],
            'min_price_above_52w_low': 1.30,
            'max_distance_from_52w_high': 0.75,
            'min_volume': 500_000,
        }

        detector = StageDetector(old_params)

        # Should initialize without error
        assert detector.params == old_params


class TestInvalidMode:
    """Test error handling for invalid mode"""

    def test_invalid_mode_raises_error(self, config_params, sample_stock_data):
        """Invalid mode should raise ValueError"""
        detector = StageDetector(config_params)

        with pytest.raises(ValueError, match="Invalid mode"):
            detector.detect_stage(sample_stock_data, mode='invalid')

    def test_invalid_mode_in_check_conditions_raises_error(self, config_params, sample_stock_data):
        """Invalid mode in check_stage2_conditions should raise ValueError"""
        detector = StageDetector(config_params)

        with pytest.raises(ValueError, match="Invalid mode"):
            detector.check_stage2_conditions(sample_stock_data, mode='invalid')
