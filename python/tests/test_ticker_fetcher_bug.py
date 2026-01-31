"""
Test-Driven Development for bug fix: KeyError on df[output_columns]

The bug occurs when filter_tickers returns data that doesn't have required columns.
Root cause: The return type contract is inconsistent between tests and implementation.
"""
import pytest
import pandas as pd
from unittest.mock import patch
import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import TickerFetcher


class TestTickerFetcherBugFix:
    """Test-Driven Development for the KeyError bug"""

    @pytest.fixture
    def fetcher(self):
        """Create a TickerFetcher instance"""
        return TickerFetcher(
            min_market_cap=1_000_000_000,
            min_price=5.0,
            min_volume=100_000,
            max_tickers=10,
            request_delay=0.0
        )

    @pytest.fixture
    def valid_ticker_data(self):
        """Sample ticker data that passes all filters"""
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
            }
        }

    def test_filter_tickers_returns_correct_structure(self, fetcher, valid_ticker_data):
        """RED: filter_tickers must return dict with 'tickers' and 'filter_stats' keys"""
        result = fetcher.filter_tickers(valid_ticker_data)
        
        # The method returns a dict, not a list
        assert isinstance(result, dict), "filter_tickers must return dict"
        assert 'tickers' in result, "Result must have 'tickers' key"
        assert 'filter_stats' in result, "Result must have 'filter_stats' key"
        
        # tickers should be a list of dicts
        filtered_list = result['tickers']
        assert isinstance(filtered_list, list), "tickers must be a list"
        assert len(filtered_list) > 0, "Should have filtered tickers"

    def test_filter_tickers_output_has_required_columns(self, fetcher, valid_ticker_data):
        """RED: Each filtered ticker must have 'ticker', 'exchange', 'sector' columns"""
        result = fetcher.filter_tickers(valid_ticker_data)
        filtered_list = result['tickers']
        
        required_columns = ['ticker', 'exchange', 'sector']
        for ticker_dict in filtered_list:
            for col in required_columns:
                assert col in ticker_dict, f"Missing required column '{col}'"
            # Verify columns have values
            assert ticker_dict['ticker'], "ticker cannot be empty"
            assert ticker_dict['exchange'], "exchange cannot be empty"
            assert ticker_dict['sector'], "sector cannot be empty"

    def test_run_produces_valid_dataframe_with_columns(self, fetcher, valid_ticker_data):
        """
        RED: The run() method must create DataFrame with required columns
        
        This is the critical test for the KeyError bug:
        KeyError: "None of [Index(['ticker', 'exchange', 'sector'], dtype='object')] are in the [columns]"
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_tickers.csv"
            
            # Mock the network calls to return consistent dict structures
            with patch.object(fetcher, 'fetch_all_tickers') as mock_fetch_all, \
                 patch.object(fetcher, 'get_ticker_info_batch') as mock_get_info:
                
                # Mock fetch_all_tickers to return dict with 'tickers' and 'stats'
                mock_fetch_all.return_value = {
                    'tickers': set(valid_ticker_data.keys()),
                    'stats': {'sp500': 0, 'nasdaq': 2, 'nyse': 0, 'russell3000': 0, 
                              'raw_total': 2, 'unique_total': 2}
                }
                
                # Mock get_ticker_info_batch to return dict with 'info' and 'stats'
                mock_get_info.return_value = {
                    'info': valid_ticker_data,
                    'stats': {'success': 2, 'failed': 0, 'total': 2}
                }
                
                # Run should not raise KeyError
                result_df = fetcher.run(output_path=str(output_path))
                
                # Verify DataFrame has required columns
                assert 'ticker' in result_df.columns
                assert 'exchange' in result_df.columns
                assert 'sector' in result_df.columns
                
                # Verify CSV was created with required columns
                assert output_path.exists()
                csv_df = pd.read_csv(output_path)
                assert 'ticker' in csv_df.columns
                assert 'exchange' in csv_df.columns
                assert 'sector' in csv_df.columns

    def test_run_handles_empty_filtered_result(self, fetcher):
        """Test that run() handles case where all tickers are filtered out"""
        empty_ticker_data = {
            'BAD_STOCK': {
                'market_cap': 100_000,  # Below minimum
                'current_price': 1.0,
                'average_volume': 1_000,
                'sector': 'Unknown',
                'quote_type': 'EQUITY',
                'exchange': 'OTC'
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_tickers.csv"
            
            with patch.object(fetcher, 'fetch_all_tickers') as mock_fetch_all, \
                 patch.object(fetcher, 'get_ticker_info_batch') as mock_get_info:
                
                mock_fetch_all.return_value = {
                    'tickers': set(empty_ticker_data.keys()),
                    'stats': {'sp500': 0, 'nasdaq': 0, 'nyse': 0, 'russell3000': 0,
                              'raw_total': 1, 'unique_total': 1}
                }
                
                mock_get_info.return_value = {
                    'info': empty_ticker_data,
                    'stats': {'success': 1, 'failed': 0, 'total': 1}
                }
                
                # Should not raise KeyError even with no passing tickers
                result_df = fetcher.run(output_path=str(output_path))
                
                # DataFrame should be empty but have the right columns
                assert len(result_df) == 0, "No tickers should pass filters"
                assert 'ticker' in result_df.columns
                assert 'exchange' in result_df.columns
                assert 'sector' in result_df.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
