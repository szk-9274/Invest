"""
Stage2Cache: Disk-based cache for Stage2 detection results

Caches Stage2 detection results to avoid re-computation for same
ticker+date+mode combinations.
"""
import json
import hashlib
import numpy as np
from pathlib import Path
from typing import Dict, Optional
from loguru import logger


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, (np.bool_, np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class Stage2Cache:
    """
    Disk-based cache for Stage2 detection results.

    Stores results as JSON files named by MD5 hash of
    ticker+date+mode combination.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the Stage2 cache.

        Args:
            cache_dir: Directory for cache files (default: cache/stage2/)
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / "cache" / "stage2"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'hit_rate': 0.0
        }

    def _get_cache_key(self, ticker: str, date_str: str, mode: str) -> str:
        """
        Generate cache key hash.

        Args:
            ticker: Ticker symbol
            date_str: Date string
            mode: Mode ('strict' or 'relaxed')

        Returns:
            MD5 hash string (32 characters)
        """
        key_str = f"{ticker}_{date_str}_{mode}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, ticker: str, date_str: str, mode: str) -> Optional[Dict]:
        """
        Retrieve cached Stage2 result.

        Args:
            ticker: Ticker symbol
            date_str: Date string
            mode: Mode ('strict' or 'relaxed')

        Returns:
            Cached result dict or None if not found
        """
        self._stats['total_requests'] += 1

        cache_key = self._get_cache_key(ticker, date_str, mode)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            self._stats['misses'] += 1
            self._update_hit_rate()
            return None

        try:
            with open(cache_file, 'r') as f:
                result = json.load(f)

            self._stats['hits'] += 1
            self._update_hit_rate()

            logger.debug(f"Cache HIT: {ticker} {date_str} {mode}")
            return result

        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Cache read error for {ticker}: {e}")
            self._stats['misses'] += 1
            self._update_hit_rate()
            return None

    def set(self, ticker: str, date_str: str, mode: str, result: Dict) -> None:
        """
        Store Stage2 result to cache.

        Args:
            ticker: Ticker symbol
            date_str: Date string
            mode: Mode ('strict' or 'relaxed')
            result: Stage2 detection result dict
        """
        cache_key = self._get_cache_key(ticker, date_str, mode)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2, cls=NumpyEncoder)

            logger.debug(f"Cache SET: {ticker} {date_str} {mode}")

        except IOError as e:
            logger.warning(f"Cache write error for {ticker}: {e}")

    def get_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dict with hits, misses, total_requests, hit_rate
        """
        return self._stats.copy()

    def clear(self) -> None:
        """
        Clear all cache files and reset statistics.
        """
        # Remove all JSON files in cache directory
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")

        # Reset statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'hit_rate': 0.0
        }

        logger.info("Cache cleared")

    def _update_hit_rate(self) -> None:
        """Update hit rate calculation."""
        if self._stats['total_requests'] > 0:
            self._stats['hit_rate'] = (
                self._stats['hits'] / self._stats['total_requests']
            )
        else:
            self._stats['hit_rate'] = 0.0
