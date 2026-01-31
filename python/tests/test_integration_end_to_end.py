"""
Integration test for the complete ticker update pipeline

Tests the full flow: fetch → normalize → get info → filter → output
"""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import TickerFetcher


class TestEndToEndIntegration:
    """Test the complete ticker update pipeline"""

    def test_complete_pipeline_with_all_phases(self):
        """Integration test: Full pipeline with normalization, rate limiting, and filtering"""
        fetcher = TickerFetcher(
            min_market_cap=1_000_000_000,
            min_price=5.0,
            request_delay=0.0
        )

        with patch.object(fetcher, 'fetch_sp500') as mock_sp500, \
             patch.object(fetcher, 'fetch_nasdaq_composite') as mock_nasdaq, \
             patch.object(fetcher, 'fetch_nyse_listed') as mock_nyse, \
             patch.object(fetcher, 'fetch_russell3000_proxy') as mock_russell:

            # Return realistic mix of valid and invalid tickers
            mock_sp500.return_value = [
                'AAPL', 'MSFT', 'GOOGL',  # Valid
                'TEST.W', 'BAD.P',  # Invalid (warrant, preferred)
            ]
            mock_nasdaq.return_value = ['TSLA', 'NVDA', 'SPAC.U']  # 1 invalid (unit)
            mock_nyse.return_value = ['JPM', 'BRK-A']  # 1 invalid (class share)
            mock_russell.return_value = []

            # Mock get_ticker_info to return valid data
            def mock_get_info(ticker):
                if ticker in ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'JPM']:
                    return {
                        'market_cap': 2_000_000_000,  # Above 1B threshold
                        'current_price': 100.0,  # Above $5
                        'average_volume': 1_000_000,  # Above 500K
                        'sector': 'Technology',
                        'industry': 'Software',
                        'quote_type': 'EQUITY',
                        'exchange': 'NASDAQ',
                        'long_name': ticker + ' Inc.'
                    }
                return None

            with patch.object(fetcher, 'get_ticker_info', side_effect=mock_get_info):
                result = fetcher.run()

                # Verify results
                assert isinstance(result, pd.DataFrame), "Should return DataFrame"
                assert len(result) == 6, f"Should have 6 valid tickers after all filters, got {len(result)}"

                # Verify all invalid tickers were filtered out
                result_tickers = set(result['ticker'].tolist())
                assert 'TEST.W' not in result_tickers, "Should filter out warrants"
                assert 'BAD.P' not in result_tickers, "Should filter out preferred"
                assert 'SPAC.U' not in result_tickers, "Should filter out units"
                assert 'BRK-A' not in result_tickers, "Should filter out class shares"

                # Verify all valid tickers passed through
                expected_tickers = {'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'JPM'}
                assert result_tickers == expected_tickers, \
                    f"Expected {expected_tickers}, got {result_tickers}"

    def test_pipeline_handles_high_failure_rate_gracefully(self):
        """Integration test: Pipeline should handle high API failure rate without crashing"""
        fetcher = TickerFetcher(
            min_market_cap=1_000_000_000,
            request_delay=0.0
        )

        with patch.object(fetcher, 'fetch_all_tickers') as mock_fetch:
            # Return many tickers
            mock_fetch.return_value = {
                'tickers': set([f'TICK{i}' for i in range(100)]),
                'stats': {
                    'sp500': 100,
                    'nasdaq': 0,
                    'nyse': 0,
                    'russell3000': 0,
                    'raw_total': 100,
                    'unique_total': 100,
                    'normalized_total': 100,
                    'excluded_by_normalization': 0
                }
            }

            # Mock get_ticker_info to fail 90% of the time
            def mock_get_info(ticker):
                idx = int(ticker.replace('TICK', ''))
                if idx % 10 == 0:  # Only 10% succeed
                    return {
                        'market_cap': 2_000_000_000,
                        'current_price': 100.0,
                        'average_volume': 1_000_000,
                        'sector': 'Technology',
                        'industry': 'Software',
                        'quote_type': 'EQUITY',
                        'exchange': 'NASDAQ',
                        'long_name': ticker
                    }
                return None

            with patch.object(fetcher, 'get_ticker_info', side_effect=mock_get_info):
                result = fetcher.run()

                # Should still return valid DataFrame, not crash
                assert isinstance(result, pd.DataFrame), "Should return DataFrame even with 90% failure rate"
                assert len(result) == 10, f"Should have 10 successful tickers, got {len(result)}"

    def test_pipeline_with_small_market_cap_filter(self):
        """Integration test: Verify relaxed market cap filter ($1B) works correctly"""
        fetcher = TickerFetcher(
            min_market_cap=1_000_000_000,  # $1B threshold
            min_price=5.0,
            request_delay=0.0
        )

        with patch.object(fetcher, 'fetch_all_tickers') as mock_fetch:
            mock_fetch.return_value = {
                'tickers': set(['LARGE', 'MEDIUM', 'SMALL']),
                'stats': {
                    'sp500': 3,
                    'nasdaq': 0,
                    'nyse': 0,
                    'russell3000': 0,
                    'raw_total': 3,
                    'unique_total': 3,
                    'normalized_total': 3,
                    'excluded_by_normalization': 0
                }
            }

            def mock_get_info(ticker):
                market_caps = {
                    'LARGE': 5_000_000_000,  # $5B - should pass
                    'MEDIUM': 1_500_000_000,  # $1.5B - should pass
                    'SMALL': 500_000_000,  # $500M - should fail
                }
                return {
                    'market_cap': market_caps[ticker],
                    'current_price': 100.0,
                    'average_volume': 1_000_000,
                    'sector': 'Technology',
                    'industry': 'Software',
                    'quote_type': 'EQUITY',
                    'exchange': 'NASDAQ',
                    'long_name': ticker
                }

            with patch.object(fetcher, 'get_ticker_info', side_effect=mock_get_info):
                result = fetcher.run()

                # Should pass LARGE and MEDIUM, filter out SMALL
                assert len(result) == 2, f"Should have 2 tickers passing $1B filter, got {len(result)}"
                result_tickers = set(result['ticker'].tolist())
                assert 'LARGE' in result_tickers
                assert 'MEDIUM' in result_tickers
                assert 'SMALL' not in result_tickers


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
