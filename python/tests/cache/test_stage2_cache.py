"""
Tests for Stage2Cache module
"""
import pytest
import sys
from pathlib import Path
import json
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cache.stage2_cache import Stage2Cache


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def cache(temp_cache_dir):
    """Create a Stage2Cache instance with temp directory"""
    return Stage2Cache(cache_dir=temp_cache_dir)


class TestCacheInitialization:
    """Test cache initialization"""

    def test_cache_initializes_with_default_dir(self):
        """Cache should initialize with default directory"""
        cache = Stage2Cache()
        assert cache.cache_dir is not None
        assert Path(cache.cache_dir).exists()

    def test_cache_initializes_with_custom_dir(self, temp_cache_dir):
        """Cache should initialize with custom directory"""
        cache = Stage2Cache(cache_dir=temp_cache_dir)
        assert str(cache.cache_dir) == str(temp_cache_dir)
        assert Path(cache.cache_dir).exists()


class TestCacheKeyGeneration:
    """Test cache key generation"""

    def test_get_cache_key_returns_consistent_hash(self, cache):
        """Same inputs should produce same cache key"""
        key1 = cache._get_cache_key("AAPL", "2024-01-15", "strict")
        key2 = cache._get_cache_key("AAPL", "2024-01-15", "strict")

        assert key1 == key2
        assert len(key1) == 32  # MD5 hash length

    def test_get_cache_key_different_for_different_inputs(self, cache):
        """Different inputs should produce different cache keys"""
        key1 = cache._get_cache_key("AAPL", "2024-01-15", "strict")
        key2 = cache._get_cache_key("MSFT", "2024-01-15", "strict")
        key3 = cache._get_cache_key("AAPL", "2024-01-16", "strict")
        key4 = cache._get_cache_key("AAPL", "2024-01-15", "relaxed")

        assert key1 != key2
        assert key1 != key3
        assert key1 != key4


class TestCacheGetSet:
    """Test cache get and set operations"""

    def test_get_returns_none_for_missing_key(self, cache):
        """Get should return None for non-existent cache entry"""
        result = cache.get("AAPL", "2024-01-15", "strict")
        assert result is None

    def test_set_and_get_stage2_result(self, cache):
        """Should be able to set and retrieve Stage2 result"""
        result = {
            'stage': 2,
            'meets_criteria': True,
            'details': {
                'price_above_sma50': True,
                'near_52w_high': True
            }
        }

        cache.set("AAPL", "2024-01-15", "strict", result)

        retrieved = cache.get("AAPL", "2024-01-15", "strict")
        assert retrieved == result

    def test_set_overwrites_existing_entry(self, cache):
        """Setting same key should overwrite previous value"""
        result1 = {'stage': 1, 'meets_criteria': False}
        result2 = {'stage': 2, 'meets_criteria': True}

        cache.set("AAPL", "2024-01-15", "strict", result1)
        cache.set("AAPL", "2024-01-15", "strict", result2)

        retrieved = cache.get("AAPL", "2024-01-15", "strict")
        assert retrieved == result2

    def test_different_modes_are_cached_separately(self, cache):
        """Strict and relaxed modes should be cached separately"""
        strict_result = {'stage': 1, 'mode': 'strict'}
        relaxed_result = {'stage': 2, 'mode': 'relaxed'}

        cache.set("AAPL", "2024-01-15", "strict", strict_result)
        cache.set("AAPL", "2024-01-15", "relaxed", relaxed_result)

        assert cache.get("AAPL", "2024-01-15", "strict") == strict_result
        assert cache.get("AAPL", "2024-01-15", "relaxed") == relaxed_result


class TestCacheStatistics:
    """Test cache statistics tracking"""

    def test_initial_stats_are_zero(self, cache):
        """Initial cache stats should be zero"""
        stats = cache.get_stats()

        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['total_requests'] == 0
        assert stats['hit_rate'] == 0.0

    def test_stats_track_cache_hits(self, cache):
        """Stats should track cache hits"""
        result = {'stage': 2}
        cache.set("AAPL", "2024-01-15", "strict", result)

        # First get - hit
        cache.get("AAPL", "2024-01-15", "strict")

        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 0
        assert stats['hit_rate'] == 1.0

    def test_stats_track_cache_misses(self, cache):
        """Stats should track cache misses"""
        # Get non-existent entry - miss
        cache.get("AAPL", "2024-01-15", "strict")

        stats = cache.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.0

    def test_stats_calculate_hit_rate_correctly(self, cache):
        """Stats should calculate hit rate correctly"""
        result = {'stage': 2}
        cache.set("AAPL", "2024-01-15", "strict", result)

        # 2 hits, 1 miss
        cache.get("AAPL", "2024-01-15", "strict")  # hit
        cache.get("AAPL", "2024-01-15", "strict")  # hit
        cache.get("MSFT", "2024-01-15", "strict")  # miss

        stats = cache.get_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['total_requests'] == 3
        assert stats['hit_rate'] == pytest.approx(0.667, abs=0.01)


class TestCacheClear:
    """Test cache clearing"""

    def test_clear_removes_all_entries(self, cache):
        """Clear should remove all cached entries"""
        cache.set("AAPL", "2024-01-15", "strict", {'stage': 2})
        cache.set("MSFT", "2024-01-15", "strict", {'stage': 1})

        cache.clear()

        assert cache.get("AAPL", "2024-01-15", "strict") is None
        assert cache.get("MSFT", "2024-01-15", "strict") is None

    def test_clear_resets_statistics(self, cache):
        """Clear should reset cache statistics"""
        cache.set("AAPL", "2024-01-15", "strict", {'stage': 2})
        cache.get("AAPL", "2024-01-15", "strict")  # Generate some stats

        cache.clear()

        stats = cache.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0


class TestCachePersistence:
    """Test cache persistence to disk"""

    def test_cache_persists_to_disk(self, cache, temp_cache_dir):
        """Cache entries should be saved to disk"""
        result = {'stage': 2, 'meets_criteria': True}
        cache.set("AAPL", "2024-01-15", "strict", result)

        # Check that cache file exists
        cache_key = cache._get_cache_key("AAPL", "2024-01-15", "strict")
        cache_file = Path(temp_cache_dir) / f"{cache_key}.json"

        assert cache_file.exists()

        # Verify file content
        with open(cache_file, 'r') as f:
            saved_data = json.load(f)

        assert saved_data == result

    def test_cache_loads_from_disk(self, temp_cache_dir):
        """New cache instance should load existing cache files"""
        # Create cache and save entry
        cache1 = Stage2Cache(cache_dir=temp_cache_dir)
        result = {'stage': 2, 'meets_criteria': True}
        cache1.set("AAPL", "2024-01-15", "strict", result)

        # Create new cache instance (should load from disk)
        cache2 = Stage2Cache(cache_dir=temp_cache_dir)
        retrieved = cache2.get("AAPL", "2024-01-15", "strict")

        assert retrieved == result
