"""
TDD test for robust S&P 500 fetch with fallback handling

Issue: Even with flavor='lxml', pd.read_html() may fail with lxml ImportError
Solution: Catch ImportError specifically and handle gracefully
"""
import pytest
from unittest.mock import patch
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import TickerFetcher


class TestSP500FetchRobust:
    """Test robust S&P 500 fetch with fallback handling"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_fetch_sp500_handles_lxml_missing_gracefully(self, fetcher):
        """RED: fetch_sp500 should handle lxml import error gracefully and return empty list"""
        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            # Simulate the actual error: ImportError from lxml
            mock_read_html.side_effect = ImportError("Missing optional dependency 'lxml'")

            result = fetcher.fetch_sp500()

            # Should handle the error gracefully
            assert isinstance(result, list), "Should return list even with lxml error"
            assert len(result) == 0, "Should return empty list when lxml is missing"

    def test_fetch_sp500_tries_with_flavor_lxml(self, fetcher):
        """GREEN: fetch_sp500 should specify flavor='lxml' parameter"""
        mock_df = pd.DataFrame({'Symbol': ['AAPL']})

        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            mock_read_html.return_value = [mock_df]

            result = fetcher.fetch_sp500()

            # Verify flavor='lxml' was specified
            assert mock_read_html.called
            call_kwargs = mock_read_html.call_args[1]
            assert call_kwargs.get('flavor') == 'lxml', "Should specify flavor='lxml'"
            assert len(result) > 0

    def test_fetch_sp500_actual_execution_handles_errors(self, fetcher):
        """INTEGRATION: Real execution should not raise unhandled exceptions"""
        # This test will actually try to fetch from Wikipedia
        # It should handle any errors gracefully
        try:
            result = fetcher.fetch_sp500()
            # Either it succeeds and returns a list
            assert isinstance(result, list), "Should always return a list"
        except Exception as e:
            # Or it fails but we handle it gracefully
            pytest.fail(f"fetch_sp500 raised unhandled exception: {type(e).__name__}: {e}")


class TestFetchAllHandlesAllErrors:
    """Test that fetch_all_tickers handles all source errors"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_fetch_all_continues_on_sp500_failure(self, fetcher):
        """GREEN: fetch_all_tickers should continue fetching from other sources if S&P 500 fails"""
        with patch.object(fetcher, 'fetch_sp500') as mock_sp500, \
             patch.object(fetcher, 'fetch_nasdaq_composite') as mock_nasdaq, \
             patch.object(fetcher, 'fetch_nyse_listed') as mock_nyse, \
             patch.object(fetcher, 'fetch_russell3000_proxy') as mock_russell:

            # S&P 500 fails
            mock_sp500.return_value = []
            # But other sources succeed
            mock_nasdaq.return_value = ['AAPL', 'MSFT']
            mock_nyse.return_value = ['JPM']
            mock_russell.return_value = ['SPY']

            result = fetcher.fetch_all_tickers()

            assert 'tickers' in result
            tickers = result['tickers']
            # Should have tickers from successful sources even though S&P 500 failed
            assert len(tickers) >= 3, "Should have tickers from other sources"
            assert 'AAPL' in tickers or 'JPM' in tickers or 'SPY' in tickers


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
