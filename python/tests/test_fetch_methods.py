"""
TDD tests for fixing network timeout and encoding issues in update_tickers_extended.py

Issues fixed:
1. pd.read_html() and pd.read_csv() don't support 'timeout' parameter - REMOVED
2. Unicode characters (✗, ⚠️) cause UnicodeEncodeError on Windows CP932 - REPLACED with [OK]/[FAIL]/[WARN]
3. Fetch methods handle errors gracefully - VERIFIED
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import pandas as pd
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import TickerFetcher


class TestFetchMethodsNoTimeout:
    """Test that fetch methods work without timeout parameter"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_fetch_sp500_no_timeout_param(self, fetcher):
        """GREEN: fetch_sp500 should not use timeout parameter"""
        mock_df = pd.DataFrame({
            'Symbol': ['AAPL', 'MSFT', 'GOOGL']
        })

        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            mock_read_html.return_value = [mock_df]

            result = fetcher.fetch_sp500()

            # Verify read_html was called without timeout param
            mock_read_html.assert_called_once()
            call_kwargs = mock_read_html.call_args[1]
            assert 'timeout' not in call_kwargs, "timeout parameter should not be used"

            assert len(result) == 3, "Should return 3 tickers"

    def test_fetch_nasdaq_no_timeout_param(self, fetcher):
        """GREEN: fetch_nasdaq_composite should not use timeout parameter"""
        mock_df = pd.DataFrame({
            'Symbol': ['AAPL', 'MSFT'],
            'Test Issue': ['N', 'N']
        })

        with patch('scripts.update_tickers_extended.pd.read_csv') as mock_read_csv:
            mock_read_csv.return_value = mock_df

            result = fetcher.fetch_nasdaq_composite()

            # Verify read_csv was called without timeout param
            mock_read_csv.assert_called_once()
            call_kwargs = mock_read_csv.call_args[1]
            assert 'timeout' not in call_kwargs, "timeout parameter should not be used"

            assert isinstance(result, list), "Should return list"

    def test_fetch_nyse_no_timeout_param(self, fetcher):
        """GREEN: fetch_nyse_listed should not use timeout parameter"""
        mock_df = pd.DataFrame({
            'ACT Symbol': ['JPM', 'BAC'],
            'Exchange': ['N', 'N'],
            'Test Issue': ['N', 'N']
        })

        with patch('scripts.update_tickers_extended.pd.read_csv') as mock_read_csv:
            mock_read_csv.return_value = mock_df

            result = fetcher.fetch_nyse_listed()

            call_kwargs = mock_read_csv.call_args[1]
            assert 'timeout' not in call_kwargs, "timeout parameter should not be used"

            assert isinstance(result, list), "Should return list"

    def test_fetch_russell_no_timeout_param(self, fetcher):
        """GREEN: fetch_russell3000_proxy should not use timeout parameter"""
        mock_df = pd.DataFrame({
            'Ticker': ['SPY', 'QQQ', 'IVV']
        })

        with patch('scripts.update_tickers_extended.pd.read_csv') as mock_read_csv:
            mock_read_csv.return_value = mock_df

            result = fetcher.fetch_russell3000_proxy()

            call_kwargs = mock_read_csv.call_args[1]
            assert 'timeout' not in call_kwargs, "timeout parameter should not be used"

    def test_fetch_all_tickers_handles_errors_gracefully(self, fetcher):
        """GREEN: fetch_all_tickers should handle errors from individual sources"""
        with patch.object(fetcher, 'fetch_sp500') as mock_sp500, \
             patch.object(fetcher, 'fetch_nasdaq_composite') as mock_nasdaq, \
             patch.object(fetcher, 'fetch_nyse_listed') as mock_nyse, \
             patch.object(fetcher, 'fetch_russell3000_proxy') as mock_russell:

            # Some sources fail, others succeed
            mock_sp500.return_value = ['AAPL']
            mock_nasdaq.return_value = []  # Empty result
            mock_nyse.return_value = ['JPM']
            mock_russell.return_value = []  # Empty result

            result = fetcher.fetch_all_tickers()

            assert isinstance(result, dict), "Should return dict"
            assert 'tickers' in result, "Should have 'tickers' key"
            assert 'stats' in result, "Should have 'stats' key"
            assert isinstance(result['tickers'], set), "tickers should be a set"
            # Should combine results from successful sources
            assert 'AAPL' in result['tickers'] or 'JPM' in result['tickers']


class TestLoggingEncodingFixed:
    """Test that logging uses ASCII-safe characters instead of unicode"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_sp500_logging_no_unicode_errors(self, fetcher):
        """GREEN: fetch_sp500 logging should not raise UnicodeEncodeError"""
        mock_df = pd.DataFrame({'Symbol': ['AAPL']})

        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            mock_read_html.return_value = [mock_df]

            # Should not raise UnicodeEncodeError
            try:
                result = fetcher.fetch_sp500()
                assert isinstance(result, list)
            except UnicodeEncodeError:
                pytest.fail("UnicodeEncodeError should not be raised with ASCII-safe logging")

    def test_error_logging_no_unicode_errors(self, fetcher):
        """GREEN: Error logging should use ASCII-safe characters"""
        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            mock_read_html.side_effect = Exception("Test error")

            # Should not raise UnicodeEncodeError even on error
            try:
                result = fetcher.fetch_sp500()
                assert isinstance(result, list)
                assert len(result) == 0, "Should return empty list on error"
            except UnicodeEncodeError:
                pytest.fail("UnicodeEncodeError should not be raised in error logging")

    def test_run_produces_valid_output_with_fixed_logging(self, fetcher):
        """INTEGRATION: Full run() should work without logging errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_tickers.csv"

            with patch.object(fetcher, 'fetch_all_tickers') as mock_fetch_all, \
                 patch.object(fetcher, 'get_ticker_info_batch') as mock_get_info:

                # Return minimal data to test
                mock_fetch_all.return_value = {
                    'tickers': {'AAPL'},
                    'stats': {'sp500': 1, 'nasdaq': 0, 'nyse': 0, 'russell3000': 0,
                              'raw_total': 1, 'unique_total': 1}
                }

                mock_get_info.return_value = {
                    'info': {
                        'AAPL': {
                            'market_cap': 3_000_000_000_000,
                            'current_price': 150.0,
                            'average_volume': 50_000_000,
                            'sector': 'Technology',
                            'industry': 'Consumer Electronics',
                            'quote_type': 'EQUITY',
                            'exchange': 'NASDAQ'
                        }
                    },
                    'stats': {'success': 1, 'failed': 0, 'total': 1}
                }

                # Should not raise UnicodeEncodeError
                try:
                    result_df = fetcher.run(output_path=str(output_path))
                    assert output_path.exists(), "CSV should be created"
                    assert len(result_df) > 0, "Should have ticker data"
                except UnicodeEncodeError:
                    pytest.fail("UnicodeEncodeError should not occur during run()")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
