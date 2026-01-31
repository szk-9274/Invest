"""
TDD test for fixing S&P 500 fetch with proper User-Agent header

Issue: HTTP 403 Forbidden from Wikipedia when fetching S&P 500 data
Solution: Add User-Agent header to request to identify as a legitimate browser
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import pandas as pd
import io

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import TickerFetcher


class TestSP500UserAgent:
    """Test that S&P 500 fetch uses proper User-Agent header"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_fetch_sp500_with_user_agent(self, fetcher):
        """RED: fetch_sp500 should use requests with User-Agent header to avoid 403"""
        # Mock requests.get to capture the call
        with patch('scripts.update_tickers_extended.requests') as mock_requests:
            # Create mock response
            mock_response = MagicMock()
            mock_response.content = b"""
            <table>
                <tr><th>Symbol</th><th>Security</th></tr>
                <tr><td>AAPL</td><td>Apple Inc.</td></tr>
                <tr><td>MSFT</td><td>Microsoft Corporation</td></tr>
            </table>
            """
            mock_response.status_code = 200
            mock_requests.get.return_value = mock_response

            result = fetcher.fetch_sp500()

            # Verify requests.get was called
            assert mock_requests.get.called, "Should use requests.get for Wikipedia fetch"
            
            # Verify User-Agent header was set
            call_kwargs = mock_requests.get.call_args[1]
            assert 'headers' in call_kwargs, "Should include headers parameter"
            assert 'User-Agent' in call_kwargs['headers'], "Should set User-Agent header"
            
            # User-Agent should look like a browser
            user_agent = call_kwargs['headers']['User-Agent']
            assert 'Mozilla' in user_agent or 'Python' in user_agent, \
                "User-Agent should identify as browser or Python script"

    def test_fetch_sp500_returns_data_with_proper_headers(self, fetcher):
        """GREEN: fetch_sp500 should successfully return tickers when using proper headers"""
        # Create a mock HTML response similar to Wikipedia's S&P 500 page
        html_content = """
        <html>
        <body>
        <table class="wikitable">
            <tr><th>Symbol</th><th>Security</th><th>GICS Sector</th></tr>
            <tr><td>AAPL</td><td>Apple Inc.</td><td>Information Technology</td></tr>
            <tr><td>MSFT</td><td>Microsoft Corporation</td><td>Information Technology</td></tr>
            <tr><td>GOOGL</td><td>Alphabet Inc. Class A</td><td>Communication Services</td></tr>
        </table>
        </body>
        </html>
        """

        with patch('scripts.update_tickers_extended.requests') as mock_requests:
            mock_response = MagicMock()
            mock_response.content = html_content.encode('utf-8')
            mock_response.text = html_content
            mock_response.status_code = 200
            mock_requests.get.return_value = mock_response

            # Mock pd.read_html to parse the mocked response
            with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
                mock_df = pd.DataFrame({
                    'Symbol': ['AAPL', 'MSFT', 'GOOGL']
                })
                mock_read_html.return_value = [mock_df]

                result = fetcher.fetch_sp500()

                # Should return at least one ticker
                assert isinstance(result, list), "Should return a list"
                assert len(result) >= 1, "Should return at least 1 ticker"
                assert 'AAPL' in result or 'MSFT' in result, "Should contain fetched tickers"

    def test_fetch_sp500_handles_403_gracefully(self, fetcher):
        """GREEN: fetch_sp500 should handle 403 Forbidden gracefully and return empty list"""
        with patch('scripts.update_tickers_extended.requests') as mock_requests:
            # Simulate 403 Forbidden error
            mock_requests.get.side_effect = Exception("HTTP Error 403: Forbidden")

            result = fetcher.fetch_sp500()

            # Should not crash, should return empty list
            assert isinstance(result, list), "Should return list even on 403 error"
            assert len(result) == 0, "Should return empty list on 403 error"


class TestRequestsWithHeaders:
    """Test that requests are made with proper headers"""

    @pytest.fixture
    def fetcher(self):
        return TickerFetcher(request_delay=0.0)

    def test_user_agent_is_set_correctly(self, fetcher):
        """GREEN: User-Agent should be a valid browser-like string"""
        with patch('scripts.update_tickers_extended.requests') as mock_requests:
            mock_response = MagicMock()
            mock_response.content = b"<table></table>"
            mock_response.status_code = 200
            mock_requests.get.return_value = mock_response

            with patch('scripts.update_tickers_extended.pd.read_html') as mock_read_html:
                mock_read_html.return_value = [pd.DataFrame({'Symbol': ['AAPL']})]
                
                fetcher.fetch_sp500()

                # Get the headers from the call
                call_kwargs = mock_requests.get.call_args[1]
                headers = call_kwargs.get('headers', {})
                user_agent = headers.get('User-Agent', '')

                # User-Agent should not be empty
                assert len(user_agent) > 0, "User-Agent should not be empty"
                # Should contain some identifier
                assert any(keyword in user_agent for keyword in ['Mozilla', 'Chrome', 'Python', 'requests']), \
                    f"User-Agent '{user_agent}' should contain browser or script identifier"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
