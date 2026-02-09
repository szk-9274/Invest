"""
Tests for Phase C: Trade Marker Data with Tooltip Information

Tests cover:
1. Marker tooltips include entry/exit date, price, P&L, holding period
2. Multiple overlapping trades handled correctly
3. Marker data structure for frontend consumption
"""
import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python"))

import pandas as pd


def _create_detailed_trade_log(path: str) -> None:
    """Create a trade_log.csv with overlapping trades for testing."""
    df = pd.DataFrame(
        {
            "date": [
                "2024-01-15",
                "2024-02-01",
                "2024-01-20",
                "2024-03-01",
                "2024-02-15",
                "2024-04-01",
            ],
            "action": ["ENTRY", "EXIT", "ENTRY", "EXIT", "ENTRY", "EXIT"],
            "ticker": ["AAPL", "AAPL", "AAPL", "AAPL", "MSFT", "MSFT"],
            "price": [150.0, 160.0, 155.0, 170.0, 200.0, 190.0],
            "shares": [100, 100, 50, 50, 75, 75],
            "pnl": [0, 1000.0, 0, 750.0, 0, -750.0],
            "capital_after": [85000, 86000, 78250, 79000, 64000, 63250],
        }
    )
    df.to_csv(path, index=False)


class TestTradeMarkerEnrichment:
    """Test enriching trade markers with tooltip data."""

    def test_get_enriched_markers_exists(self):
        """get_enriched_trade_markers should be importable."""
        from services.result_loader import get_enriched_trade_markers
        assert callable(get_enriched_trade_markers)

    def test_returns_entries_and_exits(self, tmp_path):
        """get_enriched_trade_markers should return entries and exits."""
        from services.result_loader import get_enriched_trade_markers

        csv_path = str(tmp_path / "trade_log.csv")
        _create_detailed_trade_log(csv_path)

        result = get_enriched_trade_markers(csv_path, "AAPL")
        assert "entries" in result
        assert "exits" in result

    def test_entry_markers_have_date_and_price(self, tmp_path):
        """Entry markers should include date and price."""
        from services.result_loader import get_enriched_trade_markers

        csv_path = str(tmp_path / "trade_log.csv")
        _create_detailed_trade_log(csv_path)

        result = get_enriched_trade_markers(csv_path, "AAPL")
        for entry in result["entries"]:
            assert "date" in entry
            assert "price" in entry

    def test_exit_markers_have_pnl(self, tmp_path):
        """Exit markers should include P&L information."""
        from services.result_loader import get_enriched_trade_markers

        csv_path = str(tmp_path / "trade_log.csv")
        _create_detailed_trade_log(csv_path)

        result = get_enriched_trade_markers(csv_path, "AAPL")
        for exit_marker in result["exits"]:
            assert "pnl" in exit_marker

    def test_exit_markers_have_holding_period(self, tmp_path):
        """Exit markers should include holding period in days."""
        from services.result_loader import get_enriched_trade_markers

        csv_path = str(tmp_path / "trade_log.csv")
        _create_detailed_trade_log(csv_path)

        result = get_enriched_trade_markers(csv_path, "AAPL")
        for exit_marker in result["exits"]:
            assert "holding_days" in exit_marker
            assert isinstance(exit_marker["holding_days"], int)
            assert exit_marker["holding_days"] > 0

    def test_multiple_trades_for_same_ticker(self, tmp_path):
        """Should handle multiple entry/exit pairs for the same ticker."""
        from services.result_loader import get_enriched_trade_markers

        csv_path = str(tmp_path / "trade_log.csv")
        _create_detailed_trade_log(csv_path)

        result = get_enriched_trade_markers(csv_path, "AAPL")
        # AAPL has 2 entry/exit pairs
        assert len(result["entries"]) == 2
        assert len(result["exits"]) == 2

    def test_different_ticker_returns_correct_trades(self, tmp_path):
        """Markers for MSFT should only include MSFT trades."""
        from services.result_loader import get_enriched_trade_markers

        csv_path = str(tmp_path / "trade_log.csv")
        _create_detailed_trade_log(csv_path)

        result = get_enriched_trade_markers(csv_path, "MSFT")
        assert len(result["entries"]) == 1
        assert len(result["exits"]) == 1

    def test_missing_file_returns_empty(self, tmp_path):
        """Missing file should return empty entries and exits."""
        from services.result_loader import get_enriched_trade_markers

        result = get_enriched_trade_markers(
            str(tmp_path / "nonexistent.csv"), "AAPL"
        )
        assert result["entries"] == []
        assert result["exits"] == []

    def test_exit_markers_include_entry_details(self, tmp_path):
        """Exit markers should include corresponding entry date and price."""
        from services.result_loader import get_enriched_trade_markers

        csv_path = str(tmp_path / "trade_log.csv")
        _create_detailed_trade_log(csv_path)

        result = get_enriched_trade_markers(csv_path, "AAPL")
        for exit_marker in result["exits"]:
            assert "entry_date" in exit_marker
            assert "entry_price" in exit_marker
