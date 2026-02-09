"""
Tests for Phase B-1: Result Loader Service

Tests cover:
1. Loading trade_log.csv
2. Loading ticker_stats.csv
3. Extracting top/bottom tickers
4. Handling missing files gracefully
"""
import pytest
import sys
import os
import tempfile
from pathlib import Path

# Backend must be first on path to avoid collision with python/main.py
_backend_dir = str(Path(__file__).parent.parent)
_python_dir = str(Path(__file__).parent.parent.parent / "python")
if _backend_dir in sys.path:
    sys.path.remove(_backend_dir)
sys.path.insert(0, _backend_dir)
if _python_dir not in sys.path:
    sys.path.append(_python_dir)

import pandas as pd


def _create_trade_log_csv(path: str) -> None:
    """Create a sample trade_log.csv for testing."""
    df = pd.DataFrame(
        {
            "date": [
                "2024-01-15",
                "2024-02-01",
                "2024-01-20",
                "2024-03-01",
            ],
            "action": ["ENTRY", "EXIT", "ENTRY", "EXIT"],
            "ticker": ["AAPL", "AAPL", "MSFT", "MSFT"],
            "price": [150.0, 160.0, 200.0, 190.0],
            "shares": [100, 100, 50, 50],
            "pnl": [0, 1000.0, 0, -500.0],
        }
    )
    df.to_csv(path, index=False)


def _create_ticker_stats_csv(path: str) -> None:
    """Create a sample ticker_stats.csv for testing."""
    df = pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT", "GOOG", "TSLA", "META",
                        "NFLX", "AMD", "NVDA", "BAD1", "BAD2"],
            "total_pnl": [5000, 3000, 2000, 1500, 1000,
                          -500, -1000, -1500, -2000, -3000],
            "num_trades": [10, 8, 6, 5, 4, 3, 5, 7, 4, 6],
            "win_rate": [0.7, 0.625, 0.5, 0.6, 0.5,
                         0.33, 0.4, 0.29, 0.25, 0.17],
        }
    )
    df.to_csv(path, index=False)


class TestResultLoaderTradeLog:
    """Tests for loading trade_log.csv."""

    def test_load_trade_log_returns_list(self, tmp_path):
        """load_trade_log should return a list of trade records."""
        from services.result_loader import load_trade_log

        csv_path = str(tmp_path / "trade_log.csv")
        _create_trade_log_csv(csv_path)

        result = load_trade_log(csv_path)
        assert isinstance(result, list)
        assert len(result) == 4

    def test_load_trade_log_missing_file_returns_empty(self, tmp_path):
        """load_trade_log should return empty list for missing file."""
        from services.result_loader import load_trade_log

        result = load_trade_log(str(tmp_path / "nonexistent.csv"))
        assert result == []

    def test_trade_log_records_have_expected_fields(self, tmp_path):
        """Each record should have date, action, ticker, price fields."""
        from services.result_loader import load_trade_log

        csv_path = str(tmp_path / "trade_log.csv")
        _create_trade_log_csv(csv_path)

        result = load_trade_log(csv_path)
        record = result[0]
        assert "date" in record
        assert "action" in record
        assert "ticker" in record
        assert "price" in record


class TestResultLoaderTickerStats:
    """Tests for loading ticker_stats.csv."""

    def test_load_ticker_stats_returns_list(self, tmp_path):
        """load_ticker_stats should return a list of ticker stat records."""
        from services.result_loader import load_ticker_stats

        csv_path = str(tmp_path / "ticker_stats.csv")
        _create_ticker_stats_csv(csv_path)

        result = load_ticker_stats(csv_path)
        assert isinstance(result, list)
        assert len(result) == 10

    def test_load_ticker_stats_missing_file_returns_empty(self, tmp_path):
        """load_ticker_stats should return empty list for missing file."""
        from services.result_loader import load_ticker_stats

        result = load_ticker_stats(str(tmp_path / "nonexistent.csv"))
        assert result == []


class TestTopBottomTickers:
    """Tests for extracting top/bottom performing tickers."""

    def test_get_top_bottom_tickers(self, tmp_path):
        """get_top_bottom_tickers should return top 5 and bottom 5."""
        from services.result_loader import get_top_bottom_tickers

        csv_path = str(tmp_path / "ticker_stats.csv")
        _create_ticker_stats_csv(csv_path)

        result = get_top_bottom_tickers(csv_path, top_n=5, bottom_n=5)
        assert "top" in result
        assert "bottom" in result
        assert len(result["top"]) == 5
        assert len(result["bottom"]) == 5

    def test_top_tickers_sorted_by_pnl_descending(self, tmp_path):
        """Top tickers should be sorted by total_pnl in descending order."""
        from services.result_loader import get_top_bottom_tickers

        csv_path = str(tmp_path / "ticker_stats.csv")
        _create_ticker_stats_csv(csv_path)

        result = get_top_bottom_tickers(csv_path, top_n=5, bottom_n=5)
        top_pnls = [t["total_pnl"] for t in result["top"]]
        assert top_pnls == sorted(top_pnls, reverse=True)

    def test_bottom_tickers_sorted_by_pnl_ascending(self, tmp_path):
        """Bottom tickers should be sorted by total_pnl in ascending order."""
        from services.result_loader import get_top_bottom_tickers

        csv_path = str(tmp_path / "ticker_stats.csv")
        _create_ticker_stats_csv(csv_path)

        result = get_top_bottom_tickers(csv_path, top_n=5, bottom_n=5)
        bottom_pnls = [t["total_pnl"] for t in result["bottom"]]
        assert bottom_pnls == sorted(bottom_pnls)

    def test_missing_file_returns_empty_lists(self, tmp_path):
        """Missing file should return empty top/bottom lists."""
        from services.result_loader import get_top_bottom_tickers

        result = get_top_bottom_tickers(
            str(tmp_path / "nonexistent.csv"), top_n=5, bottom_n=5
        )
        assert result["top"] == []
        assert result["bottom"] == []
