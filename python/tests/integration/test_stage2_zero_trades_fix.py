"""
Integration tests for Stage2 zero trades fix

Tests the complete system: diagnostics, config, fallback, and caching.
"""
import pytest
import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis.stage_detector import StageDetector
from analysis.stage2_diagnostics import DiagnosticsTracker, Stage2ConditionResult
from backtest.fallback_manager import FallbackManager
from cache.stage2_cache import Stage2Cache
import pandas as pd
import yaml


@pytest.fixture
def config():
    """Load test configuration"""
    config_path = Path(__file__).parent.parent.parent / "config" / "params.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestConfigurationIntegration:
    """Test configuration loading and validation"""

    def test_config_has_required_sections(self, config):
        """Config should have all required sections"""
        assert 'stage' in config
        assert 'strict' in config['stage']
        assert 'relaxed' in config['stage']
        assert 'auto_fallback_enabled' in config['stage']
        assert 'min_trades_threshold' in config['stage']

    def test_strict_relaxed_thresholds_are_different(self, config):
        """Strict and relaxed thresholds should be different"""
        strict = config['stage']['strict']
        relaxed = config['stage']['relaxed']

        # Relaxed should be easier to pass
        assert relaxed['min_price_above_52w_low'] < strict['min_price_above_52w_low']
        assert relaxed['max_distance_from_52w_high'] < strict['max_distance_from_52w_high']
        assert relaxed['rs_new_high_threshold'] < strict['rs_new_high_threshold']
        assert relaxed['min_volume'] < strict['min_volume']


class TestStageDetectorIntegration:
    """Test StageDetector with real config"""

    def test_stage_detector_loads_config_correctly(self, config):
        """StageDetector should load config correctly"""
        detector = StageDetector(config['stage'])

        assert detector.params is not None
        assert 'strict' in detector.params
        assert 'relaxed' in detector.params

    def test_stage_detector_strict_mode_is_stricter(self, config):
        """Strict mode should reject more stocks than relaxed"""
        detector = StageDetector(config['stage'])

        # Create borderline stock data (passes relaxed, fails strict)
        dates = pd.date_range('2023-01-01', periods=300, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'close': [70.0] * 300,    # 70% of 52w high
            'high': [100.0] * 300,    # 52w high
            'low': [50.0] * 300,
            'volume': [1_000_000] * 300,
            'sma_50': [65.0] * 300,   # Proper MA alignment
            'sma_150': [60.0] * 300,
            'sma_200': [55.0] * 300,
            'volume_ma_50': [400_000] * 300,  # Between strict/relaxed
        })

        # Strict mode should fail (70% < 75%)
        result_strict = detector.detect_stage(data, mode='strict', use_benchmark=False)
        assert result_strict['stage'] != 2

        # Relaxed mode should pass (70% >= 60%)
        result_relaxed = detector.detect_stage(data, mode='relaxed', use_benchmark=False)
        # May still fail due to other conditions, but near_52w_high should pass
        assert result_relaxed['details']['near_52w_high'] == True


class TestFallbackManagerIntegration:
    """Test FallbackManager with real config"""

    def test_fallback_manager_configured_from_config(self, config):
        """FallbackManager should be configurable from params.yaml"""
        stage_config = config['stage']

        manager = FallbackManager(
            auto_fallback_enabled=stage_config['auto_fallback_enabled'],
            min_trades_threshold=stage_config['min_trades_threshold']
        )

        assert manager.auto_fallback_enabled == True
        assert manager.min_trades_threshold == 1
        assert manager.current_mode == 'strict'

    def test_fallback_triggers_on_zero_trades(self, config):
        """Fallback should trigger when configured threshold not met"""
        stage_config = config['stage']

        manager = FallbackManager(
            auto_fallback_enabled=stage_config['auto_fallback_enabled'],
            min_trades_threshold=stage_config['min_trades_threshold']
        )

        # Simulate zero trades
        should_fallback = manager.should_fallback(trades_count=0)
        assert should_fallback == True

        # Trigger fallback
        manager.trigger_fallback()
        assert manager.current_mode == 'relaxed'


class TestCacheIntegration:
    """Test Stage2Cache integration"""

    def test_cache_stores_and_retrieves_stage2_results(self, temp_cache_dir):
        """Cache should store and retrieve Stage2 results"""
        cache = Stage2Cache(cache_dir=temp_cache_dir)

        result = {
            'stage': 2,
            'meets_criteria': True,
            'details': {
                'price_above_sma50': True,
                'near_52w_high': True
            }
        }

        # Store result
        cache.set("AAPL", "2024-01-15", "strict", result)

        # Retrieve result
        retrieved = cache.get("AAPL", "2024-01-15", "strict")
        assert retrieved == result

        # Check stats
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['hit_rate'] == 1.0

    def test_cache_separates_strict_and_relaxed_modes(self, temp_cache_dir):
        """Cache should store strict and relaxed separately"""
        cache = Stage2Cache(cache_dir=temp_cache_dir)

        strict_result = {'stage': 1, 'mode': 'strict'}
        relaxed_result = {'stage': 2, 'mode': 'relaxed'}

        cache.set("AAPL", "2024-01-15", "strict", strict_result)
        cache.set("AAPL", "2024-01-15", "relaxed", relaxed_result)

        assert cache.get("AAPL", "2024-01-15", "strict") == strict_result
        assert cache.get("AAPL", "2024-01-15", "relaxed") == relaxed_result


class TestDiagnosticsIntegration:
    """Test diagnostics tracking integration"""

    def test_diagnostics_track_stage2_failures(self):
        """Diagnostics should track Stage2 condition failures"""
        tracker = DiagnosticsTracker()

        # Add some failed results
        result1 = Stage2ConditionResult(
            ticker="AAPL",
            date="2024-01-15",
            conditions={
                'price_above_sma50': True,
                'near_52w_high': False,  # Failed
                'rs_new_high': False     # Failed
            },
            stage=1,
            passes=False
        )

        result2 = Stage2ConditionResult(
            ticker="MSFT",
            date="2024-01-15",
            conditions={
                'price_above_sma50': True,
                'near_52w_high': False,  # Failed again
                'rs_new_high': True
            },
            stage=1,
            passes=False
        )

        tracker.add_result(result1)
        tracker.add_result(result2)

        # Get top failures
        top_failures = tracker.get_top_failures(limit=5)

        # near_52w_high should be #1 failure (2 times)
        assert top_failures[0][0] == 'near_52w_high'
        assert top_failures[0][1] == 2


class TestEndToEndWorkflow:
    """Test complete workflow from config to result"""

    def test_complete_stage2_detection_workflow(self, config, temp_cache_dir):
        """Test complete workflow: config → detector → cache → diagnostics"""

        # 1. Load config and create components
        detector = StageDetector(config['stage'])
        cache = Stage2Cache(cache_dir=temp_cache_dir)
        tracker = DiagnosticsTracker()

        # 2. Create test stock data
        dates = pd.date_range('2023-01-01', periods=300, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'close': [100.0] * 300,
            'high': [102.0] * 300,
            'low': [50.0] * 300,
            'volume': [1_000_000] * 300,
            'sma_50': [95.0] * 300,
            'sma_150': [90.0] * 300,
            'sma_200': [85.0] * 300,
            'volume_ma_50': [800_000] * 300,
        })

        ticker = "TEST"
        date_str = "2024-01-15"
        mode = "strict"

        # 3. Check cache (should miss)
        cached_result = cache.get(ticker, date_str, mode)
        assert cached_result is None

        # 4. Run Stage2 detection
        stage_result = detector.detect_stage(data, mode=mode, use_benchmark=False)

        # 5. Store in cache
        cache.set(ticker, date_str, mode, stage_result)

        # 6. Track in diagnostics
        diagnostic_result = Stage2ConditionResult(
            ticker=ticker,
            date=date_str,
            conditions=stage_result['details'],
            stage=stage_result['stage'],
            passes=stage_result['meets_criteria']
        )
        tracker.add_result(diagnostic_result)

        # 7. Verify cache hit on second access
        cached_result = cache.get(ticker, date_str, mode)
        assert cached_result == stage_result

        # 8. Verify diagnostics
        metrics = tracker.get_metrics()
        assert metrics.total_checks == 1
        assert (metrics.final_passed == 1) == stage_result['meets_criteria']

        # 9. Verify cache stats
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['total_requests'] == 2


class TestBackwardCompatibility:
    """Test backward compatibility"""

    def test_old_config_format_still_works(self):
        """Old config format (without strict/relaxed) should still work"""
        old_config = {
            'sma_periods': [50, 150, 200],
            'min_price_above_52w_low': 1.30,
            'max_distance_from_52w_high': 0.75,
            'min_volume': 500_000,
        }

        detector = StageDetector(old_config)

        # Should work with default strict mode
        dates = pd.date_range('2023-01-01', periods=300, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'close': [100.0] * 300,
            'high': [102.0] * 300,
            'low': [50.0] * 300,
            'volume': [1_000_000] * 300,
            'sma_50': [95.0] * 300,
            'sma_150': [90.0] * 300,
            'sma_200': [85.0] * 300,
            'volume_ma_50': [800_000] * 300,
        })

        result = detector.detect_stage(data, use_benchmark=False)
        assert 'stage' in result
        assert 'meets_criteria' in result
