"""
Tests for failed ticker persistence functionality.

Following TDD approach:
1. RED: Write failing tests
2. GREEN: Implement minimal code to pass
3. REFACTOR: Improve code quality
"""
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime
import csv
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import FailedTickerTracker


class TestFailedTickerTracker:
    """Test suite for FailedTickerTracker class"""

    @pytest.fixture
    def temp_csv_path(self, tmp_path):
        """Create temporary CSV path for testing"""
        return tmp_path / "failed_tickers.csv"

    @pytest.fixture
    def tracker(self, temp_csv_path):
        """Create FailedTickerTracker instance"""
        return FailedTickerTracker(str(temp_csv_path))

    def test_tracker_initialization(self, tracker, temp_csv_path):
        """Test that tracker initializes with correct path"""
        assert tracker.csv_path == Path(temp_csv_path)

    def test_csv_created_on_first_failure(self, tracker, temp_csv_path):
        """Test that CSV file is created when first failure is recorded"""
        # Initially CSV should not exist
        assert not temp_csv_path.exists()

        # Record a failure
        tracker.record_failure("INVALID", "HTTPError", "404 Not Found")

        # Now CSV should exist
        assert temp_csv_path.exists()

    def test_failure_record_structure(self, tracker, temp_csv_path):
        """Test that failure records have correct structure"""
        tracker.record_failure("BADTICK", "TimeoutError", "Request timed out")

        # Read the CSV and verify structure
        df = pd.read_csv(temp_csv_path)
        assert list(df.columns) == ["ticker", "error_type", "error_message", "timestamp", "retry_count"]

    def test_failure_record_content(self, tracker, temp_csv_path):
        """Test that failure records contain correct data"""
        test_ticker = "FAIL1"
        test_error_type = "HTTPError"
        test_error_msg = "503 Service Unavailable"

        tracker.record_failure(test_ticker, test_error_type, test_error_msg)

        # Read and verify
        df = pd.read_csv(temp_csv_path)
        assert len(df) == 1
        assert df.iloc[0]["ticker"] == test_ticker
        assert df.iloc[0]["error_type"] == test_error_type
        assert df.iloc[0]["error_message"] == test_error_msg
        assert df.iloc[0]["retry_count"] == 1

        # Verify timestamp is recent (within last minute)
        timestamp = pd.to_datetime(df.iloc[0]["timestamp"])
        now = pd.Timestamp.now()
        assert (now - timestamp).total_seconds() < 60

    def test_multiple_failures_recorded(self, tracker, temp_csv_path):
        """Test that multiple failures are recorded sequentially"""
        tracker.record_failure("TICK1", "ParseError", "Invalid JSON")
        tracker.record_failure("TICK2", "HTTPError", "404")
        tracker.record_failure("TICK3", "TimeoutError", "Timeout")

        df = pd.read_csv(temp_csv_path)
        assert len(df) == 3
        assert list(df["ticker"]) == ["TICK1", "TICK2", "TICK3"]

    def test_same_ticker_increments_retry_count(self, tracker, temp_csv_path):
        """Test that recording the same ticker multiple times increments retry_count"""
        ticker = "RETRY"

        # First failure
        tracker.record_failure(ticker, "HTTPError", "503")
        df = pd.read_csv(temp_csv_path)
        assert df[df["ticker"] == ticker]["retry_count"].iloc[0] == 1

        # Second failure
        tracker.record_failure(ticker, "HTTPError", "503")
        df = pd.read_csv(temp_csv_path)
        retry_records = df[df["ticker"] == ticker]
        assert len(retry_records) == 2
        assert retry_records["retry_count"].iloc[-1] == 2

    def test_load_failed_tickers(self, tracker, temp_csv_path):
        """Test loading failed tickers from CSV"""
        # Record some failures
        tracker.record_failure("FAIL1", "HTTPError", "404")
        tracker.record_failure("FAIL2", "TimeoutError", "Timeout")

        # Load failed tickers
        failed_tickers = tracker.load_failed_tickers()

        assert isinstance(failed_tickers, set)
        assert "FAIL1" in failed_tickers
        assert "FAIL2" in failed_tickers
        assert len(failed_tickers) == 2

    def test_load_failed_tickers_empty_csv(self, tracker, temp_csv_path):
        """Test loading from non-existent CSV returns empty set"""
        failed_tickers = tracker.load_failed_tickers()
        assert isinstance(failed_tickers, set)
        assert len(failed_tickers) == 0

    def test_load_succeeded_tickers(self, tracker, temp_csv_path):
        """Test that we can differentiate succeeded tickers"""
        # For now, succeeded tickers are those NOT in failed list
        tracker.record_failure("FAIL1", "HTTPError", "404")

        all_tickers = {"AAPL", "GOOGL", "FAIL1", "MSFT"}
        failed = tracker.load_failed_tickers()
        succeeded = all_tickers - failed

        assert "AAPL" in succeeded
        assert "GOOGL" in succeeded
        assert "MSFT" in succeeded
        assert "FAIL1" not in succeeded

    def test_csv_safe_with_no_file(self, tracker, temp_csv_path):
        """Test that operations are safe when CSV doesn't exist"""
        assert not temp_csv_path.exists()

        # Should not raise error
        failed = tracker.load_failed_tickers()
        assert len(failed) == 0

    def test_get_retry_count(self, tracker, temp_csv_path):
        """Test getting retry count for a specific ticker"""
        ticker = "TEST"

        # No retries yet
        assert tracker.get_retry_count(ticker) == 0

        # Add failures
        tracker.record_failure(ticker, "HTTPError", "503")
        assert tracker.get_retry_count(ticker) == 1

        tracker.record_failure(ticker, "HTTPError", "503")
        assert tracker.get_retry_count(ticker) == 2

    def test_should_retry_ticker(self, tracker, temp_csv_path):
        """Test retry logic based on retry count"""
        ticker = "RETRY_TEST"
        max_retries = 3

        # Should retry when no failures
        assert tracker.should_retry(ticker, max_retries) is True

        # Add failures
        tracker.record_failure(ticker, "HTTPError", "503")
        assert tracker.should_retry(ticker, max_retries) is True

        tracker.record_failure(ticker, "HTTPError", "503")
        assert tracker.should_retry(ticker, max_retries) is True

        tracker.record_failure(ticker, "HTTPError", "503")
        assert tracker.should_retry(ticker, max_retries) is True

        # After 3 failures, should not retry
        tracker.record_failure(ticker, "HTTPError", "503")
        assert tracker.should_retry(ticker, max_retries) is False

    def test_csv_columns_order(self, tracker, temp_csv_path):
        """Test that CSV columns are in expected order"""
        tracker.record_failure("TEST", "HTTPError", "404")

        with open(temp_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            assert headers == ["ticker", "error_type", "error_message", "timestamp", "retry_count"]

    def test_unicode_error_messages(self, tracker, temp_csv_path):
        """Test that unicode characters in error messages are handled"""
        tracker.record_failure("TEST", "ParseError", "Invalid JSON: 日本語エラー")

        df = pd.read_csv(temp_csv_path)
        assert "日本語エラー" in df.iloc[0]["error_message"]

    def test_special_characters_in_ticker(self, tracker, temp_csv_path):
        """Test handling of special characters in ticker symbols"""
        # Some tickers have dashes or dots
        tracker.record_failure("BRK-A", "HTTPError", "404")
        tracker.record_failure("BF.B", "TimeoutError", "Timeout")

        failed = tracker.load_failed_tickers()
        assert "BRK-A" in failed
        assert "BF.B" in failed
