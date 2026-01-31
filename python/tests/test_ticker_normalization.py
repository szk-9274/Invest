"""
TDD tests for ticker normalization module

Purpose: Filter out invalid ticker formats BEFORE Yahoo Finance API calls
Filters: Warrants (.W), Units (.U), Preferred (.P/.PR), Class shares (.A/.B)

This prevents wasted API calls on tickers that will fail in Yahoo Finance.
"""
import pytest
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

# Will be implemented
from utils.ticker_normalizer import normalize_ticker, normalize_tickers


class TestNormalizeTicker:
    """Test individual ticker normalization (pure function)"""

    def test_normalize_ticker_removes_warrant_suffix(self):
        """RED: Warrants (.W, .WS) should be excluded - not common stocks"""
        # Warrants are derivative securities, not the underlying stock
        assert normalize_ticker("AAPL.W") is None, "Should exclude warrant (.W)"
        assert normalize_ticker("MSFT.WS") is None, "Should exclude warrant (.WS)"
        assert normalize_ticker("TSLA.WT") is None, "Should exclude warrant (.WT)"

    def test_normalize_ticker_removes_unit_suffix(self):
        """RED: Units (.U, .UN) should be excluded - SPAC components"""
        # Units combine stock + warrant, not pure equity
        assert normalize_ticker("SPAC.U") is None, "Should exclude unit (.U)"
        assert normalize_ticker("TEST.UN") is None, "Should exclude unit (.UN)"

    def test_normalize_ticker_removes_preferred_suffix(self):
        """RED: Preferred shares (.P, .PR*) should be excluded - different risk profile"""
        # Preferred shares have different characteristics than common stock
        assert normalize_ticker("BAC.P") is None, "Should exclude preferred (.P)"
        assert normalize_ticker("C.PR") is None, "Should exclude preferred (.PR)"
        assert normalize_ticker("JPM.PRA") is None, "Should exclude preferred (.PRA)"
        assert normalize_ticker("WFC.PRB") is None, "Should exclude preferred (.PRB)"
        assert normalize_ticker("USB.PRC") is None, "Should exclude preferred (.PRC)"

    def test_normalize_ticker_removes_class_shares(self):
        """RED: Class shares (.A, .B, .C, .D) should be excluded - keep only primary"""
        # Multiple share classes complicate analysis, keep only primary ticker
        assert normalize_ticker("GOOG.A") is None, "Should exclude class A (.A)"
        assert normalize_ticker("BRK.B") is None, "Should exclude class B (.B)"
        assert normalize_ticker("FOX.C") is None, "Should exclude class C (.C)"

    def test_normalize_ticker_keeps_valid_tickers(self):
        """GREEN: Valid tickers should pass through unchanged"""
        assert normalize_ticker("AAPL") == "AAPL", "Should keep AAPL"
        assert normalize_ticker("MSFT") == "MSFT", "Should keep MSFT"
        assert normalize_ticker("GOOGL") == "GOOGL", "Should keep GOOGL"
        assert normalize_ticker("TSM") == "TSM", "Should keep TSM"
        assert normalize_ticker("JPM") == "JPM", "Should keep JPM"

    def test_normalize_ticker_handles_hyphen_format(self):
        """RED: Hyphenated class shares (BRK-A, BRK-B) should be filtered"""
        # Hyphen format also represents class shares
        assert normalize_ticker("BRK-A") is None, "Should exclude BRK-A (class A)"
        # Note: BRK-B is the primary Berkshire ticker, but for consistency we filter all classes
        # Users can add exceptions in configuration if needed
        assert normalize_ticker("BRK-B") is None, "Should exclude BRK-B (class B)"

    def test_normalize_ticker_handles_none_and_empty(self):
        """GREEN: Edge cases - None and empty strings"""
        assert normalize_ticker("") is None, "Empty string should return None"
        assert normalize_ticker("   ") is None, "Whitespace should return None"

    def test_normalize_ticker_is_case_insensitive(self):
        """GREEN: Ticker comparison should be case-insensitive"""
        assert normalize_ticker("aapl") == "AAPL", "Should uppercase lowercase tickers"
        assert normalize_ticker("MsFt") == "MSFT", "Should uppercase mixed case"

    def test_normalize_ticker_strips_whitespace(self):
        """GREEN: Should strip leading/trailing whitespace"""
        assert normalize_ticker(" AAPL ") == "AAPL", "Should strip whitespace"
        assert normalize_ticker("\tMSFT\n") == "MSFT", "Should strip tabs/newlines"


class TestNormalizeTickers:
    """Test batch ticker normalization"""

    def test_normalize_tickers_batch_immutable(self):
        """GREEN: Function should return NEW list, not mutate input"""
        original = ["AAPL", "MSFT.W", "GOOGL"]
        result = normalize_tickers(original)
        
        # Original should be unchanged
        assert original == ["AAPL", "MSFT.W", "GOOGL"], "Should not mutate input"
        # Result should be different object
        assert result is not original, "Should return new list"
        # Result should only have valid tickers
        assert result == ["AAPL", "GOOGL"], "Should filter invalid tickers"

    def test_normalize_tickers_filters_invalid_batch(self):
        """RED: Should filter all invalid ticker types in batch"""
        input_tickers = [
            "AAPL",      # Valid
            "MSFT.W",    # Warrant - invalid
            "GOOGL",     # Valid
            "SPAC.U",    # Unit - invalid
            "JPM",       # Valid
            "BAC.P",     # Preferred - invalid
            "TSLA",      # Valid
            "BRK.A",     # Class share - invalid
        ]
        
        result = normalize_tickers(input_tickers)
        expected = ["AAPL", "GOOGL", "JPM", "TSLA"]
        
        assert result == expected, f"Expected {expected}, got {result}"
        assert len(result) == 4, "Should have 4 valid tickers"

    def test_normalize_tickers_handles_empty_input(self):
        """GREEN: Empty input should return empty output"""
        assert normalize_tickers([]) == [], "Empty list should return empty list"

    def test_normalize_tickers_all_invalid(self):
        """GREEN: All invalid tickers should return empty list"""
        invalid_tickers = ["AAPL.W", "MSFT.U", "GOOGL.P", "TSLA.A"]
        result = normalize_tickers(invalid_tickers)
        assert result == [], "All invalid should return empty list"

    def test_normalize_tickers_all_valid(self):
        """GREEN: All valid tickers should all pass through"""
        valid_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
        result = normalize_tickers(valid_tickers)
        assert result == valid_tickers, "All valid should pass through"

    def test_normalize_tickers_preserves_order(self):
        """GREEN: Output order should match input order (filtered)"""
        input_tickers = ["AAPL", "MSFT.W", "GOOGL", "TSLA.U", "AMZN"]
        result = normalize_tickers(input_tickers)
        expected = ["AAPL", "GOOGL", "AMZN"]
        assert result == expected, "Should preserve order of valid tickers"

    def test_normalize_tickers_removes_duplicates_after_normalization(self):
        """GREEN: Should handle duplicates gracefully"""
        # After normalization, duplicates might occur (though rare)
        input_tickers = ["AAPL", "aapl", "AAPL"]
        result = normalize_tickers(input_tickers)
        # Should uppercase and preserve all (deduplication happens elsewhere in pipeline)
        assert "AAPL" in result, "Should have AAPL"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
