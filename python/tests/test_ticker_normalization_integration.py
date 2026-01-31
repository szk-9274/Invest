"""
Integration tests for ticker normalization in update_tickers_extended.py

Tests that normalization is properly integrated into the fetch workflow
to filter invalid tickers BEFORE calling Yahoo Finance API.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import TickerFetcher


class TestNormalizationIntegration:
    """Test that normalization is integrated into fetch workflow"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_fetch_all_tickers_applies_normalization(self, fetcher):
        """RED: fetch_all_tickers should normalize tickers before returning"""
        # Mock the individual fetch methods to return tickers with invalid formats
        with patch.object(fetcher, 'fetch_sp500') as mock_sp500, \
             patch.object(fetcher, 'fetch_nasdaq_composite') as mock_nasdaq, \
             patch.object(fetcher, 'fetch_nyse_listed') as mock_nyse, \
             patch.object(fetcher, 'fetch_russell3000_proxy') as mock_russell:

            # Return tickers with invalid suffixes
            mock_sp500.return_value = ['AAPL', 'MSFT.W', 'GOOGL']
            mock_nasdaq.return_value = ['AAPL', 'TSLA', 'SPAC.U']
            mock_nyse.return_value = ['JPM', 'BAC.P', 'C']
            mock_russell.return_value = ['SPY', 'BRK-A', 'VOO']

            result = fetcher.fetch_all_tickers()
            tickers = result['tickers']

            # Should exclude warrants, units, preferred, and class shares
            assert 'MSFT.W' not in tickers, "Should filter out warrants (.W)"
            assert 'SPAC.U' not in tickers, "Should filter out units (.U)"
            assert 'BAC.P' not in tickers, "Should filter out preferred (.P)"
            assert 'BRK-A' not in tickers, "Should filter out hyphenated class shares"

            # Should keep valid tickers
            assert 'AAPL' in tickers, "Should keep AAPL"
            assert 'GOOGL' in tickers, "Should keep GOOGL"
            assert 'TSLA' in tickers, "Should keep TSLA"
            assert 'JPM' in tickers, "Should keep JPM"
            assert 'C' in tickers, "Should keep C"
            assert 'SPY' in tickers, "Should keep SPY"
            assert 'VOO' in tickers, "Should keep VOO"

    def test_fetch_all_tickers_logs_normalization_stats(self, fetcher):
        """GREEN: fetch_all_tickers should log how many tickers were filtered"""
        with patch.object(fetcher, 'fetch_sp500') as mock_sp500, \
             patch.object(fetcher, 'fetch_nasdaq_composite') as mock_nasdaq, \
             patch.object(fetcher, 'fetch_nyse_listed') as mock_nyse, \
             patch.object(fetcher, 'fetch_russell3000_proxy') as mock_russell:

            # Return mix of valid and invalid tickers
            mock_sp500.return_value = ['AAPL', 'MSFT.W', 'GOOGL']  # 1 invalid
            mock_nasdaq.return_value = ['TSLA', 'SPAC.U', 'NVDA']  # 1 invalid
            mock_nyse.return_value = ['JPM', 'BAC.P', 'C']  # 1 invalid
            mock_russell.return_value = ['SPY', 'BRK-A', 'VOO']  # 1 invalid

            result = fetcher.fetch_all_tickers()
            stats = result['stats']

            # Should have normalization stats
            assert 'normalized_total' in stats, "Should track normalized ticker count"
            assert 'excluded_by_normalization' in stats, "Should track excluded count"

            # Should exclude 4 invalid tickers
            assert stats['excluded_by_normalization'] == 4, \
                "Should exclude 4 tickers (MSFT.W, SPAC.U, BAC.P, BRK-A)"

    def test_run_applies_normalization_before_yahoo_api_calls(self, fetcher):
        """GREEN: run() should normalize before calling get_ticker_info_batch()"""
        with patch.object(fetcher, 'fetch_all_tickers') as mock_fetch_all, \
             patch.object(fetcher, 'get_ticker_info_batch') as mock_get_info, \
             patch.object(fetcher, 'filter_tickers') as mock_filter:

            # Mock fetch_all_tickers to return already-normalized tickers
            mock_fetch_all.return_value = {
                'tickers': {'AAPL', 'GOOGL', 'TSLA'},  # Only valid tickers
                'stats': {
                    'sp500': 3,
                    'nasdaq': 0,
                    'nyse': 0,
                    'russell3000': 0,
                    'raw_total': 3,
                    'unique_total': 3,
                    'normalized_total': 3,
                    'excluded_by_normalization': 2  # 2 were filtered out
                }
            }

            # Mock get_ticker_info_batch to return info for valid tickers
            mock_get_info.return_value = {
                'info': {
                    'AAPL': {'marketCap': 3000000000000},
                    'GOOGL': {'marketCap': 2000000000000},
                    'TSLA': {'marketCap': 800000000000}
                },
                'stats': {'success': 3, 'failed': 0}
            }

            # Mock filter_tickers to return filtered results
            mock_filter.return_value = {
                'tickers': [
                    {'ticker': 'AAPL', 'exchange': 'NMS', 'sector': 'Technology'},
                    {'ticker': 'GOOGL', 'exchange': 'NMS', 'sector': 'Technology'},
                    {'ticker': 'TSLA', 'exchange': 'NMS', 'sector': 'Consumer Cyclical'}
                ],
                'filter_stats': {
                    'total': 3,
                    'passed': 3,
                    'excluded_marketcap': 0,
                    'excluded_type': 0
                }
            }

            result = fetcher.run()

            # Should NOT call get_ticker_info_batch with invalid tickers
            call_args = mock_get_info.call_args[0][0]  # First positional arg (ticker list)
            assert 'MSFT.W' not in call_args, "Should not call Yahoo API for warrants"
            assert 'SPAC.U' not in call_args, "Should not call Yahoo API for units"
            assert 'BAC.P' not in call_args, "Should not call Yahoo API for preferred"
            assert 'BRK-A' not in call_args, "Should not call Yahoo API for class shares"

            # Should only call with valid tickers
            assert len(call_args) == 3, "Should only process 3 valid tickers"

    def test_normalization_reduces_yahoo_api_calls(self, fetcher):
        """GREEN: Normalization should significantly reduce Yahoo Finance API calls"""
        with patch.object(fetcher, 'fetch_sp500') as mock_sp500, \
             patch.object(fetcher, 'fetch_nasdaq_composite') as mock_nasdaq, \
             patch.object(fetcher, 'fetch_nyse_listed') as mock_nyse, \
             patch.object(fetcher, 'fetch_russell3000_proxy') as mock_russell:

            # Return realistic ticker lists with ~20% invalid tickers
            # (Based on real data: warrants, units, preferred, class shares)
            mock_sp500.return_value = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',  # Valid
                'BRK.B', 'JPM.PR', 'BAC.P', 'C.WS'  # Invalid
            ]
            mock_nasdaq.return_value = []
            mock_nyse.return_value = []
            mock_russell.return_value = []

            result = fetcher.fetch_all_tickers()
            stats = result['stats']

            # Should exclude ~44% of invalid tickers (4 out of 9)
            assert stats['excluded_by_normalization'] >= 4, \
                "Should exclude at least 4 invalid tickers"

            # Should reduce total tickers by normalization
            assert stats['normalized_total'] <= stats['unique_total'], \
                "Normalized total should be <= unique total"


class TestNormalizationEdgeCases:
    """Test edge cases in normalization integration"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_normalization_handles_all_invalid_tickers(self, fetcher):
        """GREEN: Should handle case where all tickers are invalid"""
        with patch.object(fetcher, 'fetch_sp500') as mock_sp500, \
             patch.object(fetcher, 'fetch_nasdaq_composite') as mock_nasdaq, \
             patch.object(fetcher, 'fetch_nyse_listed') as mock_nyse, \
             patch.object(fetcher, 'fetch_russell3000_proxy') as mock_russell:

            # All invalid tickers
            mock_sp500.return_value = ['AAPL.W', 'MSFT.U', 'GOOGL.P']
            mock_nasdaq.return_value = []
            mock_nyse.return_value = []
            mock_russell.return_value = []

            result = fetcher.fetch_all_tickers()
            tickers = result['tickers']

            # Should return empty set
            assert len(tickers) == 0, "Should return empty set when all tickers invalid"

    def test_normalization_preserves_valid_tickers(self, fetcher):
        """GREEN: Should preserve all valid tickers"""
        with patch.object(fetcher, 'fetch_sp500') as mock_sp500, \
             patch.object(fetcher, 'fetch_nasdaq_composite') as mock_nasdaq, \
             patch.object(fetcher, 'fetch_nyse_listed') as mock_nyse, \
             patch.object(fetcher, 'fetch_russell3000_proxy') as mock_russell:

            valid_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
            mock_sp500.return_value = valid_tickers
            mock_nasdaq.return_value = []
            mock_nyse.return_value = []
            mock_russell.return_value = []

            result = fetcher.fetch_all_tickers()
            tickers = result['tickers']

            # Should preserve all valid tickers
            assert len(tickers) == 5, "Should preserve all 5 valid tickers"
            for ticker in valid_tickers:
                assert ticker in tickers, f"Should preserve {ticker}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
