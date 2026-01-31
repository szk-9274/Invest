"""
TDD test for fixing S&P 500 fetch issue with lxml parser

Issue: ImportError: Missing optional dependency 'lxml'
Solution: Specify 'lxml' parser explicitly in pd.read_html()

The test ensures that fetch_sp500() successfully fetches at least 1 ticker.
"""
import pytest
from unittest.mock import patch
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import TickerFetcher


class TestSP500Fetch:
    """Test S&P 500 fetch with proper parser"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_fetch_sp500_uses_lxml_parser(self, fetcher):
        """RED: fetch_sp500 must specify 'lxml' as the parser"""
        # Create mock data as if fetched from Wikipedia
        mock_df = pd.DataFrame({
            'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
        })

        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            # Mock the successful response
            mock_read_html.return_value = [mock_df]

            result = fetcher.fetch_sp500()

            # Verify that read_html was called with 'lxml' parser
            mock_read_html.assert_called_once()
            call_kwargs = mock_read_html.call_args[1]
            assert 'flavor' in call_kwargs or 'parser' in call_kwargs, \
                "read_html must specify parser (lxml, html5lib, or bs4)"

            # Verify we got tickers
            assert isinstance(result, list), "Should return list of tickers"
            assert len(result) > 0, "Should fetch at least 1 ticker"

    def test_fetch_sp500_returns_at_least_one_ticker(self, fetcher):
        """GREEN: fetch_sp500 should successfully fetch and return tickers"""
        # Mock successful S&P 500 data
        mock_df = pd.DataFrame({
            'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'FB']
        })

        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            mock_read_html.return_value = [mock_df]

            result = fetcher.fetch_sp500()

            # Critical assertion: at least 1 ticker fetched
            assert len(result) >= 1, "Must fetch at least 1 ticker from S&P 500"
            assert 'AAPL' in result, "Should contain AAPL"

    def test_fetch_sp500_handles_lxml_import_error(self, fetcher):
        """GREEN: fetch_sp500 should handle lxml ImportError gracefully"""
        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            # Simulate missing lxml error
            mock_read_html.side_effect = ImportError("Missing optional dependency 'lxml'")

            result = fetcher.fetch_sp500()

            # Should return empty list on error, not crash
            assert isinstance(result, list), "Should return list even on error"
            assert len(result) == 0, "Should return empty list on import error"

    def test_fetch_sp500_with_dot_symbol_conversion(self, fetcher):
        """GREEN: fetch_sp500 should convert dots to dashes in symbols"""
        # Some S&P 500 companies have dots in their symbols (BRK.A, BRK.B)
        mock_df = pd.DataFrame({
            'Symbol': ['AAPL', 'BRK.A', 'BRK.B', 'GOOGL']
        })

        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            mock_read_html.return_value = [mock_df]

            result = fetcher.fetch_sp500()

            assert len(result) == 4, "Should have 4 tickers"
            # Verify dots are converted to dashes
            assert 'BRK-A' in result, "BRK.A should be converted to BRK-A"
            assert 'BRK-B' in result, "BRK.B should be converted to BRK-B"
            assert 'BRK.A' not in result, "Original dots should not remain"


class TestFetchAllWithSP500:
    """Test fetch_all_tickers includes S&P 500 data"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_fetch_all_tickers_includes_sp500_data(self, fetcher):
        """GREEN: fetch_all_tickers should successfully include S&P 500 tickers"""
        with patch.object(fetcher, 'fetch_sp500') as mock_sp500, \
             patch.object(fetcher, 'fetch_nasdaq_composite') as mock_nasdaq, \
             patch.object(fetcher, 'fetch_nyse_listed') as mock_nyse, \
             patch.object(fetcher, 'fetch_russell3000_proxy') as mock_russell:

            # Mock at least one successful S&P 500 ticker
            mock_sp500.return_value = ['AAPL']
            mock_nasdaq.return_value = []
            mock_nyse.return_value = []
            mock_russell.return_value = []

            result = fetcher.fetch_all_tickers()

            assert isinstance(result, dict), "Should return dict"
            assert 'tickers' in result, "Should have 'tickers' key"
            tickers = result['tickers']
            assert len(tickers) > 0, "Should have at least one ticker from S&P 500"
            assert 'AAPL' in tickers, "Should contain the mocked AAPL ticker"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
