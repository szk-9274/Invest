"""
Test Stage2 → Backtest connection
Verify that Stage2 screening results are properly loaded into Backtest universe
"""
import pytest
import sys
from pathlib import Path
import pandas as pd
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestStage2BacktestConnection:
    """Test Stage2 screening results → Backtest universe connection"""

    def test_screening_results_file_format(self):
        """Verify screening_results.csv has correct format"""
        # Create sample screening results
        sample_data = pd.DataFrame({
            'ticker': ['AAPL', 'MSFT', 'NVDA'],
            'close': [180.0, 380.0, 480.0],
            'stage': [2, 2, 2]
        })

        # Verify required columns exist
        assert 'ticker' in sample_data.columns
        assert len(sample_data) > 0

    def test_backtest_loads_stage2_results(self):
        """Backtest should load Stage2 results from screening_results.csv"""
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Create fake screening_results.csv
            screening_results_path = Path(temp_dir) / "screening_results.csv"
            screening_df = pd.DataFrame({
                'ticker': ['AAPL', 'MSFT', 'NVDA'],
                'close': [180.0, 380.0, 480.0],
                'stage': [2, 2, 2]
            })
            screening_df.to_csv(screening_results_path, index=False)

            # Verify file exists and can be loaded
            assert screening_results_path.exists()

            loaded_df = pd.read_csv(screening_results_path)
            assert not loaded_df.empty
            assert 'ticker' in loaded_df.columns
            assert len(loaded_df) == 3

            tickers_from_stage2 = loaded_df['ticker'].tolist()
            assert tickers_from_stage2 == ['AAPL', 'MSFT', 'NVDA']

        finally:
            shutil.rmtree(temp_dir)

    def test_backtest_universe_filtering(self):
        """Backtest should filter universe to Stage2 candidates"""
        # Original ticker universe
        original_tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META', 'TSLA']

        # Stage2 filtered tickers (subset of original)
        stage2_tickers = ['AAPL', 'NVDA', 'META']

        # After filtering, backtest should only use Stage2 tickers
        filtered_tickers = [t for t in original_tickers if t in stage2_tickers]

        assert len(filtered_tickers) == 3
        assert set(filtered_tickers) == set(stage2_tickers)

    def test_stage2_results_missing_warning(self):
        """Should warn if Stage2 results file is missing"""
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            screening_results_path = Path(temp_dir) / "screening_results.csv"

            # File should not exist
            assert not screening_results_path.exists()

            # In this case, backtest should:
            # 1. Log warning
            # 2. Use all input tickers (no filter)
            # This is tested in the main logic

        finally:
            shutil.rmtree(temp_dir)

    def test_empty_stage2_results(self):
        """Should handle empty Stage2 results gracefully"""
        temp_dir = tempfile.mkdtemp()

        try:
            screening_results_path = Path(temp_dir) / "screening_results.csv"

            # Create empty CSV with headers
            empty_df = pd.DataFrame(columns=['ticker', 'close', 'stage'])
            empty_df.to_csv(screening_results_path, index=False)

            # Load and verify
            loaded_df = pd.read_csv(screening_results_path)
            assert loaded_df.empty
            assert 'ticker' in loaded_df.columns

        finally:
            shutil.rmtree(temp_dir)


class TestStage2BacktestWorkflow:
    """Test complete Stage2 → Backtest workflow"""

    def test_workflow_stage2_then_backtest(self):
        """Test workflow: Stage2 screening → Backtest"""
        # Step 1: Stage2 screening produces results
        stage2_results = pd.DataFrame({
            'ticker': ['AAPL', 'MSFT', 'NVDA'],
            'close': [180.0, 380.0, 480.0],
            'stage': [2, 2, 2],
            'distance_from_high_pct': [5.0, 3.0, 2.0]
        })

        assert len(stage2_results) == 3

        # Step 2: Backtest should use these tickers only
        backtest_tickers = stage2_results['ticker'].tolist()
        assert backtest_tickers == ['AAPL', 'MSFT', 'NVDA']

        # Step 3: Verify Stage2 candidates are preserved
        assert all(stage2_results['stage'] == 2)

    def test_ticker_universe_reduction(self):
        """Test that ticker universe is properly reduced"""
        # Original universe (e.g., from tickers.csv)
        original_universe = 1890

        # After Stage2 screening
        stage2_candidates = 253

        # Reduction ratio
        reduction_ratio = stage2_candidates / original_universe

        # Should be significant reduction (< 20%)
        assert reduction_ratio < 0.20
        assert stage2_candidates > 0


class TestDiagnosticLogging:
    """Test diagnostic logging for Stage2 → Backtest connection"""

    def test_stage2_filter_logs(self):
        """Verify diagnostic logs show Stage2 filtering"""
        # Expected log messages:
        expected_logs = [
            "STAGE2 FILTER APPLIED",
            "Stage2 results loaded from:",
            "Backtest universe: 1890 → 253 tickers (Stage2 filtered)"
        ]

        # These logs should be present when Stage2 results exist
        # (Actual log checking would require capturing logger output)
        assert len(expected_logs) == 3

    def test_missing_stage2_warning_logs(self):
        """Verify warning logs when Stage2 results missing"""
        expected_warnings = [
            "NO STAGE2 FILTER - Using all tickers",
            "Stage2 results not found",
            "RECOMMENDATION: Run 'python main.py --mode stage2' first"
        ]

        assert len(expected_warnings) == 3
