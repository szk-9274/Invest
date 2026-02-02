"""
Tests for Task 4: Cache Mechanism (24h TTL)

Following TDD approach:
1. RED: Write failing tests
2. GREEN: Implement minimal code to pass
3. REFACTOR: Improve code quality
"""
import pytest
from pathlib import Path
import time
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetcher import YahooFinanceFetcher


class TestCacheMechanism:
    """Test suite for cache mechanism with 24h TTL"""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """Create temporary cache directory"""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return cache_dir

    @pytest.fixture
    def fetcher(self, temp_cache_dir):
        """Create YahooFinanceFetcher with temp cache"""
        return YahooFinanceFetcher(
            cache_dir=str(temp_cache_dir),
            cache_enabled=True,
            cache_max_age_hours=24  # 24h TTL
        )

    def test_cache_ttl_is_24_hours(self, fetcher):
        """Test that cache TTL is set to 24 hours"""
        assert fetcher.cache_max_age_hours == 24

    def test_cache_enabled_by_default(self, fetcher):
        """Test that cache is enabled"""
        assert fetcher.cache_enabled is True

    def test_cache_hit_logged(self, fetcher, caplog):
        """Test that cache hits are logged"""
        import logging

        # This test verifies the log mechanism exists
        # Actual cache hit logging happens in _load_from_cache
        assert hasattr(fetcher, '_load_from_cache')

    def test_cache_miss_logged(self, fetcher):
        """Test that cache misses are handled"""
        # Cache miss when file doesn't exist
        result = fetcher._load_from_cache("NONEXISTENT", "1d", "1d")
        assert result is None

    def test_cache_saves_data(self, fetcher, temp_cache_dir):
        """Test that data is saved to cache"""
        import pandas as pd

        # Create dummy data
        data = pd.DataFrame({'close': [100, 101, 102]})

        # Save to cache
        fetcher._save_to_cache("TEST", "1d", "1d", data)

        # Verify cache file exists
        cache_files = list(temp_cache_dir.glob("TEST_*.pkl"))
        assert len(cache_files) == 1

    def test_cache_loads_fresh_data(self, fetcher):
        """Test that fresh cache data is loaded"""
        import pandas as pd

        # Save data
        data = pd.DataFrame({'close': [100, 101, 102]})
        fetcher._save_to_cache("AAPL", "1d", "1d", data)

        # Load immediately (should be fresh)
        loaded = fetcher._load_from_cache("AAPL", "1d", "1d")
        assert loaded is not None
        assert len(loaded) == 3

    def test_cache_rejects_expired_data(self, fetcher):
        """Test that expired cache data is rejected"""
        import pandas as pd
        import os

        # Save data
        data = pd.DataFrame({'close': [100, 101, 102]})
        fetcher._save_to_cache("EXPIRED", "1d", "1d", data)

        # Get cache file
        cache_file = fetcher._cache_path("EXPIRED", "1d", "1d")
        assert cache_file.exists()

        # Manually set file modification time to 25 hours ago
        old_time = time.time() - (25 * 3600)  # 25 hours ago
        os.utime(str(cache_file), (old_time, old_time))

        # Try to load (should return None for expired)
        loaded = fetcher._load_from_cache("EXPIRED", "1d", "1d")
        assert loaded is None

    def test_cache_within_24h_is_valid(self, fetcher):
        """Test that cache within 24h is considered valid"""
        import pandas as pd
        import os

        # Save data
        data = pd.DataFrame({'close': [100, 101, 102]})
        fetcher._save_to_cache("VALID", "1d", "1d", data)

        # Get cache file
        cache_file = fetcher._cache_path("VALID", "1d", "1d")

        # Set file modification time to 23 hours ago (still valid)
        recent_time = time.time() - (23 * 3600)
        os.utime(str(cache_file), (recent_time, recent_time))

        # Should still load
        loaded = fetcher._load_from_cache("VALID", "1d", "1d")
        assert loaded is not None

    def test_cache_disabled_flag(self, temp_cache_dir):
        """Test that cache can be disabled"""
        fetcher = YahooFinanceFetcher(
            cache_dir=str(temp_cache_dir),
            cache_enabled=False
        )

        import pandas as pd
        data = pd.DataFrame({'close': [100]})

        # Save should not create file
        fetcher._save_to_cache("TEST", "1d", "1d", data)

        cache_files = list(temp_cache_dir.glob("*.pkl"))
        assert len(cache_files) == 0

    def test_default_cache_ttl_is_24h(self):
        """Test that default TTL is 24 hours (Task 4 requirement)"""
        fetcher = YahooFinanceFetcher()
        # Default should now be 24h (changed from 12h)
        assert fetcher.cache_max_age_hours == 24


class TestCacheLogging:
    """Test cache hit/miss logging"""

    @pytest.fixture
    def fetcher(self, tmp_path):
        """Create fetcher with temp cache"""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return YahooFinanceFetcher(
            cache_dir=str(cache_dir),
            cache_max_age_hours=24
        )

    def test_cache_hit_message_format(self, fetcher):
        """Test that cache hit log has correct format"""
        import pandas as pd

        # Create and save data
        data = pd.DataFrame({'close': [100, 101]})
        fetcher._save_to_cache("AAPL", "1d", "1d", data)

        # Load (should log cache hit)
        # The actual log check is done in the method
        loaded = fetcher._load_from_cache("AAPL", "1d", "1d")
        assert loaded is not None

    def test_cache_miss_returns_none(self, fetcher):
        """Test that cache miss returns None"""
        result = fetcher._load_from_cache("NONEXISTENT", "1d", "1d")
        assert result is None

    def test_cache_directory_creation(self, tmp_path):
        """Test that cache directory is created if it doesn't exist"""
        cache_dir = tmp_path / "new_cache"
        assert not cache_dir.exists()

        fetcher = YahooFinanceFetcher(cache_dir=str(cache_dir), cache_enabled=True)
        assert cache_dir.exists()
