"""
Smoke test for scripts/update_tickers_extended.py

Purpose: Prevent KeyError on CSV output columns (ticker, exchange, sector)
Strategy: Mock network calls, verify DataFrame structure and CSV output contract
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import TickerFetcher


class TestTickerFetcherSmokeTest:
    """Minimal smoke test to ensure TickerFetcher produces valid output"""

    @pytest.fixture
    def mock_ticker_fetcher(self):
        """Create TickerFetcher instance with minimal config"""
        return TickerFetcher(
            min_market_cap=1_000_000_000,
            min_price=5.0,
            min_volume=100_000,
            max_tickers=10,
            request_delay=0.0  # No delay for tests
        )

    @pytest.fixture
    def sample_ticker_info(self):
        """Sample ticker info data for testing"""
        return {
            'AAPL': {
                'market_cap': 3_000_000_000_000,
                'current_price': 150.0,
                'average_volume': 50_000_000,
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'quote_type': 'EQUITY',
                'exchange': 'NASDAQ',
                'long_name': 'Apple Inc.'
            },
            'MSFT': {
                'market_cap': 2_500_000_000_000,
                'current_price': 380.0,
                'average_volume': 25_000_000,
                'sector': 'Technology',
                'industry': 'Software',
                'quote_type': 'EQUITY',
                'exchange': 'NASDAQ',
                'long_name': 'Microsoft Corporation'
            },
            'JPM': {
                'market_cap': 500_000_000_000,
                'current_price': 160.0,
                'average_volume': 10_000_000,
                'sector': 'Financial Services',
                'industry': 'Banks',
                'quote_type': 'EQUITY',
                'exchange': 'NYSE',
                'long_name': 'JPMorgan Chase & Co.'
            }
        }

    def test_filter_tickers_returns_required_columns(self, mock_ticker_fetcher, sample_ticker_info):
        """
        CRITICAL TEST: Verify filter_tickers returns list with required columns

        This test prevents KeyError on CSV output:
        - ticker (required for identification)
        - exchange (required for CSV output)
        - sector (required for CSV output)
        """
        # Execute filter
        result = mock_ticker_fetcher.filter_tickers(sample_ticker_info)

        # Verify structure (current version returns list directly)
        assert isinstance(result, list), "filter_tickers must return a list"
        assert len(result) > 0, "Should have at least one ticker after filtering"

        # CRITICAL: Verify required columns exist in each ticker dict
        required_columns = ['ticker', 'exchange', 'sector']
        for ticker_dict in result:
            for col in required_columns:
                assert col in ticker_dict, f"Missing required column '{col}' in ticker dict"

        # Verify all tickers passed filtering
        assert len(result) == 3, "All sample tickers should pass filtering"

    def test_filter_tickers_excludes_below_thresholds(self, mock_ticker_fetcher):
        """Verify filtering logic excludes stocks below thresholds"""
        # Create data with one stock below each threshold
        test_data = {
            'LOW_MCAP': {
                'market_cap': 500_000_000,  # Below 1B threshold
                'current_price': 10.0,
                'average_volume': 1_000_000,
                'sector': 'Technology',
                'quote_type': 'EQUITY',
                'exchange': 'NASDAQ'
            },
            'LOW_PRICE': {
                'market_cap': 2_000_000_000,
                'current_price': 3.0,  # Below $5 threshold
                'average_volume': 1_000_000,
                'sector': 'Technology',
                'quote_type': 'EQUITY',
                'exchange': 'NASDAQ'
            },
            'LOW_VOLUME': {
                'market_cap': 2_000_000_000,
                'current_price': 10.0,
                'average_volume': 50_000,  # Below 100K threshold
                'sector': 'Technology',
                'quote_type': 'EQUITY',
                'exchange': 'NASDAQ'
            },
            'EXCLUDED_TYPE': {
                'market_cap': 2_000_000_000,
                'current_price': 10.0,
                'average_volume': 1_000_000,
                'sector': 'Technology',
                'quote_type': 'ETF',  # Excluded type
                'exchange': 'NASDAQ'
            }
        }

        result = mock_ticker_fetcher.filter_tickers(test_data)

        # All should be filtered out (current version returns list)
        assert isinstance(result, list), "filter_tickers must return a list"
        assert len(result) == 0, "All test tickers should be filtered out"

    def test_run_produces_valid_dataframe_structure(self, mock_ticker_fetcher, sample_ticker_info, tmp_path):
        """
        INTEGRATION SMOKE TEST: Verify run() produces DataFrame with correct CSV structure

        This is the critical contract test to prevent KeyError on:
        df_output = df[output_columns]  # output_columns = ['ticker', 'exchange', 'sector']
        """
        # Mock all network calls
        with patch.object(mock_ticker_fetcher, 'fetch_all_tickers') as mock_fetch_all, \
             patch.object(mock_ticker_fetcher, 'get_ticker_info_batch') as mock_get_info:

            # Mock fetch_all_tickers to return sample tickers (current version returns Set[str])
            mock_fetch_all.return_value = set(sample_ticker_info.keys())

            # Mock get_ticker_info_batch to return sample info (current version returns Dict)
            mock_get_info.return_value = sample_ticker_info

            # Run with temporary output path
            output_path = tmp_path / "test_tickers.csv"
            result_df = mock_ticker_fetcher.run(output_path=str(output_path))

            # CRITICAL: Verify DataFrame has required columns for CSV output
            required_columns = ['ticker', 'exchange', 'sector']
            for col in required_columns:
                assert col in result_df.columns, f"Output DataFrame missing required column '{col}'"

            # Verify CSV file was created
            assert output_path.exists(), "CSV file should be created"

            # Verify CSV can be read back
            csv_df = pd.read_csv(output_path)
            for col in required_columns:
                assert col in csv_df.columns, f"CSV output missing required column '{col}'"

            # Verify data integrity
            assert len(csv_df) == len(result_df), "CSV should have same rows as DataFrame"
            assert len(csv_df) > 0, "CSV should have at least one row"

    def test_fetch_methods_return_lists(self, mock_ticker_fetcher):
        """Smoke test: Verify fetch methods return list type (even if empty)"""
        with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
            # Mock Wikipedia to return empty
            mock_read_html.side_effect = Exception("Network error")

            result = mock_ticker_fetcher.fetch_sp500()
            assert isinstance(result, list), "fetch_sp500 should return list even on error"
            assert len(result) == 0, "Should return empty list on error"

        with patch('scripts.update_tickers_extended.pd.read_csv') as mock_read_csv:
            # Mock NASDAQ to return empty
            mock_read_csv.side_effect = Exception("Network error")

            result = mock_ticker_fetcher.fetch_nasdaq_composite()
            assert isinstance(result, list), "fetch_nasdaq_composite should return list even on error"
            assert len(result) == 0, "Should return empty list on error"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
