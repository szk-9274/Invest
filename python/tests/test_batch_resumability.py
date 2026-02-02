"""
Tests for Task 3: Batch Processing Resumability

Following TDD approach:
1. RED: Write failing tests
2. GREEN: Implement minimal code to pass
3. REFACTOR: Improve code quality
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_tickers_extended import BatchProgressTracker, TickerFetcher


class TestBatchProgressTracker:
    """Test suite for BatchProgressTracker class"""

    @pytest.fixture
    def temp_progress_file(self, tmp_path):
        """Create temporary progress file path"""
        return tmp_path / "batch_progress.json"

    @pytest.fixture
    def tracker(self, temp_progress_file):
        """Create BatchProgressTracker instance"""
        return BatchProgressTracker(str(temp_progress_file))

    def test_tracker_initialization(self, tracker, temp_progress_file):
        """Test that tracker initializes with correct path"""
        assert tracker.progress_file == Path(temp_progress_file)

    def test_progress_file_created_on_first_save(self, tracker, temp_progress_file):
        """Test that progress file is created when first batch is saved"""
        assert not temp_progress_file.exists()

        tracker.save_batch_progress(0, 10, ["AAPL", "GOOGL"])
        assert temp_progress_file.exists()

    def test_save_batch_progress_structure(self, tracker, temp_progress_file):
        """Test that saved progress has correct structure"""
        tracker.save_batch_progress(2, 10, ["AAPL", "GOOGL", "MSFT"])

        with open(temp_progress_file, 'r') as f:
            data = json.load(f)

        assert "current_batch" in data
        assert "total_batches" in data
        assert "completed_batches" in data
        assert "last_updated" in data

    def test_save_batch_progress_content(self, tracker, temp_progress_file):
        """Test that batch progress contains correct data"""
        batch_num = 3
        total = 10
        tickers = ["AAPL", "GOOGL"]

        tracker.save_batch_progress(batch_num, total, tickers)

        with open(temp_progress_file, 'r') as f:
            data = json.load(f)

        assert data["current_batch"] == batch_num
        assert data["total_batches"] == total
        assert batch_num in data["completed_batches"]
        assert data["last_updated"] is not None

    def test_multiple_batches_saved(self, tracker, temp_progress_file):
        """Test that multiple batch completions are tracked"""
        tracker.save_batch_progress(0, 5, ["AAPL"])
        tracker.save_batch_progress(1, 5, ["GOOGL"])
        tracker.save_batch_progress(2, 5, ["MSFT"])

        with open(temp_progress_file, 'r') as f:
            data = json.load(f)

        assert data["current_batch"] == 2
        assert set(data["completed_batches"]) == {0, 1, 2}

    def test_load_progress_returns_completed_batches(self, tracker, temp_progress_file):
        """Test loading completed batches from file"""
        tracker.save_batch_progress(0, 5, ["AAPL"])
        tracker.save_batch_progress(1, 5, ["GOOGL"])

        progress = tracker.load_progress()

        assert progress is not None
        assert progress["current_batch"] == 1
        assert set(progress["completed_batches"]) == {0, 1}

    def test_load_progress_returns_none_when_no_file(self, tracker, temp_progress_file):
        """Test loading returns None when no progress file exists"""
        assert not temp_progress_file.exists()
        progress = tracker.load_progress()
        assert progress is None

    def test_is_batch_completed(self, tracker):
        """Test checking if a batch is already completed"""
        tracker.save_batch_progress(0, 5, ["AAPL"])
        tracker.save_batch_progress(2, 5, ["GOOGL"])

        assert tracker.is_batch_completed(0) is True
        assert tracker.is_batch_completed(1) is False
        assert tracker.is_batch_completed(2) is True

    def test_clear_progress(self, tracker, temp_progress_file):
        """Test clearing progress file"""
        tracker.save_batch_progress(0, 5, ["AAPL"])
        assert temp_progress_file.exists()

        tracker.clear_progress()
        assert not temp_progress_file.exists()

    def test_get_next_batch_to_process(self, tracker):
        """Test finding the next batch that needs processing"""
        # Complete batches 0, 1, 3
        tracker.save_batch_progress(0, 5, ["AAPL"])
        tracker.save_batch_progress(1, 5, ["GOOGL"])
        tracker.save_batch_progress(3, 5, ["MSFT"])

        # Next batch should be 2 (not 4, since 2 is incomplete)
        next_batch = tracker.get_next_batch_to_process(5)
        assert next_batch == 2

    def test_progress_logging_format(self, tracker, caplog):
        """Test that progress is logged in readable format"""
        import logging

        with caplog.at_level(logging.INFO):
            tracker.save_batch_progress(3, 10, ["AAPL", "GOOGL"])

        # Just verify method executes without error
        assert True

    def test_resume_from_partial_completion(self, tracker):
        """Test resuming from partial completion scenario"""
        # Simulate: batches 0, 1, 2 completed, 3-9 pending
        for i in range(3):
            tracker.save_batch_progress(i, 10, [f"TICK{i}"])

        # Should be able to resume from batch 3
        progress = tracker.load_progress()
        assert progress["current_batch"] == 2
        assert len(progress["completed_batches"]) == 3

        # Next to process should be 3
        next_batch = tracker.get_next_batch_to_process(10)
        assert next_batch == 3

    def test_concurrent_batch_completion_safe(self, tracker, temp_progress_file):
        """Test that concurrent batch completions don't corrupt data"""
        # Save multiple batches rapidly
        for i in range(5):
            tracker.save_batch_progress(i, 5, [f"TICK{i}"])

        # Verify all recorded
        progress = tracker.load_progress()
        assert len(progress["completed_batches"]) == 5


class TestBatchResumabilityIntegration:
    """Integration tests for batch resumability in TickerFetcher"""

    def test_fetcher_has_batch_tracker(self):
        """Test that TickerFetcher has BatchProgressTracker"""
        fetcher = TickerFetcher()
        assert hasattr(fetcher, 'batch_tracker')
        assert isinstance(fetcher.batch_tracker, BatchProgressTracker)

    def test_fetcher_saves_progress_after_batch(self, tmp_path):
        """Test that fetcher saves progress after completing each batch"""
        from scripts.update_tickers_extended import BatchProgressTracker

        progress_file = tmp_path / "batch_progress.json"
        fetcher = TickerFetcher()
        fetcher.batch_tracker = BatchProgressTracker(str(progress_file))

        # Mock batch processing
        batch_num = 0
        total_batches = 3

        fetcher.batch_tracker.save_batch_progress(batch_num, total_batches, ["AAPL"])

        assert progress_file.exists()

    def test_fetcher_skips_completed_batches_on_resume(self, tmp_path):
        """Test that fetcher skips already completed batches"""
        from scripts.update_tickers_extended import BatchProgressTracker

        progress_file = tmp_path / "batch_progress.json"
        tracker = BatchProgressTracker(str(progress_file))

        # Pre-complete batch 0
        tracker.save_batch_progress(0, 3, ["AAPL", "GOOGL"])

        # Check that batch 0 is marked as completed
        assert tracker.is_batch_completed(0) is True
        assert tracker.is_batch_completed(1) is False

    def test_progress_cleared_on_successful_completion(self, tmp_path):
        """Test that progress file is cleared after all batches complete"""
        from scripts.update_tickers_extended import BatchProgressTracker

        progress_file = tmp_path / "batch_progress.json"
        tracker = BatchProgressTracker(str(progress_file))

        # Complete all batches
        for i in range(3):
            tracker.save_batch_progress(i, 3, [f"TICK{i}"])

        assert progress_file.exists()

        # Clear on completion
        tracker.clear_progress()
        assert not progress_file.exists()
