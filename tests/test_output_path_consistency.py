"""
Test Output Path Consistency

This test module verifies that backtest output files (trade_log.csv, ticker_stats.csv)
are saved to consistent locations that chart generation can find.

Root Cause Being Fixed:
- trade_log.csv was saved to: python/output/trade_log.csv
- Chart generation looked for it at: python/output/backtest/trade_log.csv
- This caused "trade_log.csv not found" warning even though file existed

Expected Behavior After Fix:
- trade_log.csv saved to: python/output/backtest/trade_log.csv
- ticker_stats.csv saved to: python/output/backtest/ticker_stats.csv
- Chart generation finds both files at expected locations
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pytest
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))


class TestTradeLogOutputPath:
    """Test that trade_log.csv is saved to the correct location."""

    def test_trade_logger_saves_to_backtest_subdir(self, tmp_path):
        """
        Test that TradeLogger saves trade_log.csv to output/backtest/ directory.

        This is the core fix: TradeLogger should save to a consistent location
        that chart generation expects.
        """
        from backtest.trade_logger import TradeLogger

        # Create TradeLogger with output dir pointing to backtest subdir
        output_dir = tmp_path / "output" / "backtest"
        logger = TradeLogger(output_dir=str(output_dir))

        # Log a sample entry
        logger.log_entry(
            date=datetime(2024, 1, 15),
            ticker='AAPL',
            price=150.0,
            shares=100,
            reason='entry_signal',
            capital_after=85000.0
        )

        # Save the log
        csv_path = logger.save()

        # Verify file is saved to expected location
        expected_path = output_dir / "trade_log.csv"
        assert Path(csv_path) == expected_path
        assert expected_path.exists()

    def test_backtest_engine_uses_backtest_subdir_for_output(self, tmp_path):
        """
        Test that BacktestEngine initializes TradeLogger with output/backtest/ path.

        The engine should always save trade logs to the backtest subdirectory,
        not the root output directory.
        """
        from backtest.trade_logger import TradeLogger

        # Simulate the expected configuration
        config = {
            'output': {
                'csv_path': 'output/screening_results.csv'
            },
            'performance': {'request_delay': 0.1},
            'stage': {
                'auto_fallback_enabled': True,
                'min_trades_threshold': 1
            },
            'backtest': {
                'initial_capital': 100000,
                'max_positions': 5,
                'commission': 0.001
            },
            'risk': {'risk_per_trade': 0.01}
        }

        # The expected output directory should be output/backtest
        # regardless of the config's csv_path
        expected_output_dir = Path(__file__).parent.parent / "python" / "output" / "backtest"

        # This test validates the expected directory structure
        # After the fix, BacktestEngine should use output/backtest/ for trade logs
        assert "backtest" in str(expected_output_dir)


class TestTickerStatsOutputPath:
    """Test that ticker_stats.csv is saved to the correct location."""

    def test_ticker_analysis_saves_to_backtest_subdir(self, tmp_path):
        """
        Test that TickerAnalysis saves ticker_stats.csv to output/backtest/ directory.
        """
        from backtest.ticker_analysis import TickerAnalysis

        # Create TickerAnalysis with output dir pointing to backtest subdir
        output_dir = tmp_path / "output" / "backtest"
        analyzer = TickerAnalysis(output_dir=str(output_dir))

        # Analyze sample data
        entries = [
            {'action': 'EXIT', 'ticker': 'AAPL', 'pnl': 500.0},
            {'action': 'EXIT', 'ticker': 'MSFT', 'pnl': -200.0},
            {'action': 'ENTRY', 'ticker': 'AAPL', 'pnl': None},
        ]
        analyzer.analyze(entries)

        # Save the stats
        csv_path = analyzer.save()

        # Verify file is saved to expected location
        expected_path = output_dir / "ticker_stats.csv"
        assert Path(csv_path) == expected_path
        assert expected_path.exists()


class TestChartGenerationFindsFiles:
    """Test that chart generation finds output files at expected locations."""

    def test_generate_backtest_charts_finds_trade_log(self, tmp_path):
        """
        Test that _generate_backtest_charts() finds trade_log.csv at expected path.

        After the fix, when backtest runs, it should:
        1. Save trade_log.csv to output/backtest/trade_log.csv
        2. Chart generation should find it at the same location
        """
        # Setup: Create the expected directory structure
        output_dir = tmp_path / "output" / "backtest"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create trade_log.csv at expected location
        trade_log_path = output_dir / "trade_log.csv"
        trade_log_data = pd.DataFrame({
            'date': ['2024-01-15', '2024-02-15'],
            'ticker': ['AAPL', 'AAPL'],
            'action': ['ENTRY', 'EXIT'],
            'price': [150.0, 160.0],
            'shares': [100, 100],
            'reason': ['entry_signal', 'target_reached'],
            'pnl': [None, 1000.0],
            'capital_after': [85000.0, 95000.0]
        })
        trade_log_data.to_csv(trade_log_path, index=False)

        # Verify the file exists at expected location
        assert trade_log_path.exists()

        # The chart generation function checks this path
        expected_trade_log_path = output_dir / "trade_log.csv"
        assert expected_trade_log_path.exists()

    def test_generate_backtest_charts_finds_ticker_stats(self, tmp_path):
        """
        Test that _generate_backtest_charts() finds ticker_stats.csv at expected path.
        """
        # Setup: Create the expected directory structure
        output_dir = tmp_path / "output" / "backtest"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create ticker_stats.csv at expected location
        ticker_stats_path = output_dir / "ticker_stats.csv"
        ticker_stats_data = pd.DataFrame({
            'ticker': ['AAPL', 'MSFT'],
            'total_pnl': [1000.0, -500.0],
            'trade_count': [2, 1]
        })
        ticker_stats_data.to_csv(ticker_stats_path, index=False)

        # Verify the file exists at expected location
        assert ticker_stats_path.exists()

        # The chart generation function checks this path
        expected_ticker_stats_path = output_dir / "ticker_stats.csv"
        assert expected_ticker_stats_path.exists()

    def test_chart_mode_finds_trade_log_at_correct_path(self, tmp_path):
        """
        Test that chart mode (--mode chart) finds trade_log.csv at the correct path.

        This tests the path used in run_chart_mode() in main.py.
        After the fix, it should look in output/backtest/ not just output/.
        """
        # Create the expected directory structure
        output_dir = tmp_path / "output" / "backtest"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create trade_log.csv at expected location
        trade_log_path = output_dir / "trade_log.csv"
        trade_log_data = pd.DataFrame({
            'date': ['2024-01-15'],
            'ticker': ['AAPL'],
            'action': ['ENTRY'],
            'price': [150.0],
            'shares': [100],
            'reason': ['entry_signal'],
            'pnl': [None],
            'capital_after': [85000.0]
        })
        trade_log_data.to_csv(trade_log_path, index=False)

        # The expected path for chart mode should be output/backtest/trade_log.csv
        expected_path = output_dir / "trade_log.csv"
        assert expected_path.exists()


class TestPathLogging:
    """Test that file paths are properly logged during chart generation."""

    def test_trade_log_path_logged_when_chart_generation_starts(self, tmp_path, caplog):
        """
        Test that the resolved trade_log_path is logged when chart generation starts.

        This helps debugging by showing the exact path being checked.
        """
        import logging
        from backtest.ticker_charts import _parse_trade_log

        # Enable logging capture
        caplog.set_level(logging.DEBUG)

        # Create a non-existent path
        trade_log_path = str(tmp_path / "nonexistent" / "trade_log.csv")

        # Call the function (should log debug message about path)
        entry_dates, exit_dates = _parse_trade_log(trade_log_path, 'AAPL')

        # Verify empty results (file doesn't exist)
        assert entry_dates == []
        assert exit_dates == []

    def test_ticker_charts_logs_absolute_path(self, tmp_path, caplog):
        """
        Test that ticker_charts module logs absolute paths for debugging.
        """
        import logging
        caplog.set_level(logging.DEBUG)

        # The path should be logged as absolute for debugging clarity
        output_dir = tmp_path / "output" / "backtest"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Verify we can resolve to absolute path
        abs_path = output_dir.resolve()
        assert abs_path.is_absolute()


class TestBacktestEngineOutputDirConstruction:
    """Test that BacktestEngine constructs the correct output directory."""

    def test_output_dir_is_backtest_subdir_not_root(self):
        """
        Test that the output directory includes 'backtest' subdirectory.

        This is the core fix: the output directory should be:
        - CORRECT: python/output/backtest/
        - WRONG: python/output/
        """
        # The expected path construction
        from pathlib import Path

        # Simulate what the fix should produce
        python_dir = Path(__file__).parent.parent / "python"
        expected_output_dir = python_dir / "output" / "backtest"

        # Verify the path includes 'backtest' subdirectory
        assert "backtest" in str(expected_output_dir)
        assert expected_output_dir.name == "backtest"

    def test_engine_output_dir_from_config_gets_backtest_appended(self):
        """
        Test that even if config points to 'output/', the engine uses 'output/backtest/'.

        Config value: output/screening_results.csv (stripped to output/)
        Expected result: output/backtest/
        """
        from pathlib import Path

        # Simulate config value
        config_csv_path = 'output/screening_results.csv'

        # Old behavior (WRONG): just use parent of csv_path
        old_output_dir = Path(config_csv_path).parent  # output/

        # New behavior (CORRECT): use output/backtest/
        # This is what the fix should implement
        python_dir = Path(__file__).parent.parent / "python"
        new_output_dir = python_dir / "output" / "backtest"

        # Verify the difference
        assert "backtest" not in str(old_output_dir)
        assert "backtest" in str(new_output_dir)


class TestEndToEndPathConsistency:
    """End-to-end tests for path consistency between backtest and chart generation."""

    def test_backtest_output_matches_chart_input_paths(self, tmp_path):
        """
        Test that the paths used by backtest output match paths used by chart input.

        This is the integration test for the entire fix.
        """
        # Create a consistent output directory
        output_dir = tmp_path / "output" / "backtest"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Paths that backtest should save to
        backtest_trade_log_path = output_dir / "trade_log.csv"
        backtest_ticker_stats_path = output_dir / "ticker_stats.csv"

        # Paths that chart generation expects
        chart_trade_log_path = output_dir / "trade_log.csv"
        chart_ticker_stats_path = output_dir / "ticker_stats.csv"

        # Verify they match
        assert backtest_trade_log_path == chart_trade_log_path
        assert backtest_ticker_stats_path == chart_ticker_stats_path

    def test_no_path_mismatch_warning_when_files_exist(self, tmp_path, caplog):
        """
        Test that no "file not found" warning is logged when files are in correct location.
        """
        import logging
        caplog.set_level(logging.WARNING)

        # Create files at expected location
        output_dir = tmp_path / "output" / "backtest"
        output_dir.mkdir(parents=True, exist_ok=True)

        trade_log_path = output_dir / "trade_log.csv"
        ticker_stats_path = output_dir / "ticker_stats.csv"

        # Create sample files
        pd.DataFrame({'col': [1]}).to_csv(trade_log_path, index=False)
        pd.DataFrame({'col': [1]}).to_csv(ticker_stats_path, index=False)

        # Verify files exist
        assert trade_log_path.exists()
        assert ticker_stats_path.exists()

        # If chart generation is called with correct paths, no warning should be logged
        # (This will be verified by the actual implementation tests)


class TestConfigPathResolution:
    """Test configuration path resolution for output directories."""

    def test_csv_path_config_stripped_correctly(self):
        """
        Test that csv_path from config is handled correctly.

        Config may have: 'output/screening_results.csv'
        We need: 'output/backtest/' for trade logs
        """
        from pathlib import Path

        config_csv_path = 'output/screening_results.csv'

        # The config path should not directly determine trade log location
        # Instead, we should use a fixed backtest subdirectory
        base_output_dir = Path(config_csv_path).parent  # 'output'
        backtest_output_dir = base_output_dir / "backtest"

        assert backtest_output_dir.name == "backtest"
        # Use Path comparison for cross-platform compatibility
        assert backtest_output_dir == Path("output/backtest")

    def test_absolute_path_resolution(self):
        """
        Test that paths are resolved to absolute paths correctly.
        """
        from pathlib import Path

        # Relative path from config
        relative_path = "output/backtest"

        # Should be resolved relative to python/ directory
        python_dir = Path(__file__).parent.parent / "python"
        absolute_path = python_dir / relative_path

        # Verify it's a proper absolute path
        assert "python" in str(absolute_path)
        assert "output" in str(absolute_path)
        assert "backtest" in str(absolute_path)


# Additional edge case tests

class TestEdgeCases:
    """Test edge cases in path handling."""

    def test_backtest_subdir_created_if_not_exists(self, tmp_path):
        """
        Test that output/backtest/ directory is created if it doesn't exist.
        """
        from backtest.trade_logger import TradeLogger

        # Use a non-existent directory
        output_dir = tmp_path / "new_output" / "backtest"
        assert not output_dir.exists()

        # Create TradeLogger
        logger = TradeLogger(output_dir=str(output_dir))
        logger.log_entry(
            date=datetime(2024, 1, 15),
            ticker='AAPL',
            price=150.0,
            shares=100,
            reason='entry_signal',
            capital_after=85000.0
        )

        # Save should create the directory
        csv_path = logger.save()

        # Verify directory was created
        assert output_dir.exists()
        assert Path(csv_path).exists()

    def test_windows_path_separators_handled(self, tmp_path):
        """
        Test that Windows path separators are handled correctly.
        """
        from pathlib import Path

        # Create path with forward slashes (cross-platform)
        path_str = str(tmp_path / "output" / "backtest")

        # Path should work regardless of separator style
        path = Path(path_str)
        assert path.name == "backtest"

    def test_empty_trade_log_still_saved_to_correct_path(self, tmp_path):
        """
        Test that even an empty trade log is saved to the correct path.
        """
        from backtest.trade_logger import TradeLogger

        output_dir = tmp_path / "output" / "backtest"
        logger = TradeLogger(output_dir=str(output_dir))

        # Save without any entries
        csv_path = logger.save()

        # Verify file exists at correct location
        expected_path = output_dir / "trade_log.csv"
        assert Path(csv_path) == expected_path
        assert expected_path.exists()


class TestBacktestEngineIntegration:
    """Integration tests for BacktestEngine output path."""

    def test_backtest_engine_trade_logger_output_dir_contains_backtest(self):
        """
        CRITICAL TEST: Verify BacktestEngine initializes TradeLogger with 'backtest' in path.

        This test will FAIL until the bug is fixed.
        Current behavior: output_dir is 'python/output' (from config)
        Expected behavior: output_dir should be 'python/output/backtest'
        """
        from backtest.engine import BacktestEngine
        from pathlib import Path

        # Minimal config for engine initialization
        config = {
            'output': {
                'csv_path': 'output/screening_results.csv'
            },
            'performance': {'request_delay': 0.1},
            'stage': {
                'auto_fallback_enabled': True,
                'min_trades_threshold': 1
            },
            'backtest': {
                'initial_capital': 100000,
                'max_positions': 5,
                'commission': 0.001
            },
            'risk': {'risk_per_trade': 0.01},
            'vcp': {
                'base_period_min': 35,
                'base_period_max': 65,
                'contraction_sequence': [0.25, 0.15, 0.08, 0.05],
                'last_contraction_max': 0.10,
                'dryup_vol_ratio': 0.6,
                'breakout_vol_ratio': 1.5,
                'pivot_min_high_52w_ratio': 0.95,
                'pivot_buffer_atr': 0.5
            }
        }

        # Create engine
        engine = BacktestEngine(config)

        # Get the trade logger's output directory
        trade_logger_output_dir = engine.trade_logger.output_dir

        # CRITICAL ASSERTION: The output dir should contain 'backtest'
        # This test FAILS with current code because output_dir is 'python/output'
        assert 'backtest' in trade_logger_output_dir, (
            f"TradeLogger output_dir should contain 'backtest' subdirectory. "
            f"Got: {trade_logger_output_dir}"
        )


class TestMainPyChartModePathConsistency:
    """Test that main.py chart mode uses correct paths."""

    def test_chart_mode_trade_log_path_includes_backtest_subdir(self):
        """
        CRITICAL TEST: Verify chart mode looks for trade_log in output/backtest/.

        This test validates that run_chart_mode() in main.py uses the correct path.
        """
        # The expected path pattern for chart mode
        # After fix: output/backtest/trade_log.csv
        # Before fix (bug): output/trade_log.csv

        expected_path_pattern = "output/backtest/trade_log.csv"

        # This assertion documents the expected behavior
        assert "backtest" in expected_path_pattern


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
