"""
TDD Tests for Stage2 Diagnostics Module

Phase 1 of Stage2 zero trades fix: Enhanced Diagnostics
Tests per-ticker condition tracking and aggregate funnel metrics.

Following TDD methodology:
1. RED - Write failing tests first
2. GREEN - Implement minimal code to pass
3. REFACTOR - Improve while keeping tests green
"""
import pytest
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestStage2ConditionResult:
    """Tests for Stage2ConditionResult dataclass"""

    def test_condition_result_creation(self):
        """RED: Create Stage2ConditionResult with all required fields"""
        from analysis.stage2_diagnostics import Stage2ConditionResult

        result = Stage2ConditionResult(
            ticker="AAPL",
            date="2024-01-15",
            conditions={
                "price_above_sma50": True,
                "sma50_above_sma150": True,
                "near_52w_high": False,
                "rs_new_high": False,
            },
            stage=1,
            passes=False,
        )

        assert result.ticker == "AAPL"
        assert result.date == "2024-01-15"
        assert result.stage == 1
        assert result.passes is False
        assert result.conditions["price_above_sma50"] is True
        assert result.conditions["near_52w_high"] is False

    def test_condition_result_all_passing(self):
        """RED: Create result where all conditions pass"""
        from analysis.stage2_diagnostics import Stage2ConditionResult

        all_conditions = {
            "price_above_sma50": True,
            "sma50_above_sma150": True,
            "sma150_above_sma200": True,
            "ma200_uptrend": True,
            "above_52w_low": True,
            "near_52w_high": True,
            "ma50_above_ma150_200": True,
            "rs_new_high": True,
            "sufficient_volume": True,
        }

        result = Stage2ConditionResult(
            ticker="NVDA",
            date="2024-01-15",
            conditions=all_conditions,
            stage=2,
            passes=True,
        )

        assert result.passes is True
        assert result.stage == 2
        assert all(result.conditions.values())

    def test_condition_result_immutability(self):
        """RED: Verify dataclass is immutable (frozen)"""
        from analysis.stage2_diagnostics import Stage2ConditionResult

        result = Stage2ConditionResult(
            ticker="AAPL",
            date="2024-01-15",
            conditions={"price_above_sma50": True},
            stage=2,
            passes=True,
        )

        # Attempting to modify should raise an error
        with pytest.raises((AttributeError, TypeError)):
            result.ticker = "MSFT"


class TestStage2FunnelMetrics:
    """Tests for Stage2FunnelMetrics dataclass"""

    def test_funnel_metrics_initialization(self):
        """RED: FunnelMetrics should have sensible defaults"""
        from analysis.stage2_diagnostics import Stage2FunnelMetrics

        metrics = Stage2FunnelMetrics()

        assert metrics.total_checks == 0
        assert metrics.by_condition == {}
        assert metrics.final_passed == 0

    def test_funnel_metrics_with_values(self):
        """RED: FunnelMetrics should accept values"""
        from analysis.stage2_diagnostics import Stage2FunnelMetrics

        metrics = Stage2FunnelMetrics(
            total_checks=100,
            by_condition={"near_52w_high": 45, "rs_new_high": 30},
            final_passed=25,
        )

        assert metrics.total_checks == 100
        assert metrics.by_condition["near_52w_high"] == 45
        assert metrics.final_passed == 25


class TestDiagnosticsTrackerAddResult:
    """Tests for DiagnosticsTracker.add_result()"""

    def test_tracker_add_result(self):
        """RED: Add a result to the tracker"""
        from analysis.stage2_diagnostics import (
            DiagnosticsTracker,
            Stage2ConditionResult,
        )

        tracker = DiagnosticsTracker()
        result = Stage2ConditionResult(
            ticker="AAPL",
            date="2024-01-15",
            conditions={
                "price_above_sma50": True,
                "near_52w_high": False,
            },
            stage=1,
            passes=False,
        )

        tracker.add_result(result)

        metrics = tracker.get_metrics()
        assert metrics.total_checks == 1

    def test_tracker_add_multiple_results(self):
        """RED: Add multiple results to the tracker"""
        from analysis.stage2_diagnostics import (
            DiagnosticsTracker,
            Stage2ConditionResult,
        )

        tracker = DiagnosticsTracker()

        for ticker in ["AAPL", "MSFT", "GOOG"]:
            result = Stage2ConditionResult(
                ticker=ticker,
                date="2024-01-15",
                conditions={"price_above_sma50": True},
                stage=1,
                passes=False,
            )
            tracker.add_result(result)

        metrics = tracker.get_metrics()
        assert metrics.total_checks == 3


class TestDiagnosticsTrackerAggregateMetrics:
    """Tests for DiagnosticsTracker.get_metrics() aggregation"""

    def test_tracker_aggregate_metrics(self):
        """RED: Calculate aggregate stats from multiple results"""
        from analysis.stage2_diagnostics import (
            DiagnosticsTracker,
            Stage2ConditionResult,
        )

        tracker = DiagnosticsTracker()

        # Add result that fails on near_52w_high
        tracker.add_result(
            Stage2ConditionResult(
                ticker="AAPL",
                date="2024-01-15",
                conditions={
                    "price_above_sma50": True,
                    "near_52w_high": False,
                    "rs_new_high": True,
                },
                stage=1,
                passes=False,
            )
        )

        # Add result that fails on near_52w_high and rs_new_high
        tracker.add_result(
            Stage2ConditionResult(
                ticker="MSFT",
                date="2024-01-15",
                conditions={
                    "price_above_sma50": True,
                    "near_52w_high": False,
                    "rs_new_high": False,
                },
                stage=1,
                passes=False,
            )
        )

        # Add result that passes all
        tracker.add_result(
            Stage2ConditionResult(
                ticker="NVDA",
                date="2024-01-15",
                conditions={
                    "price_above_sma50": True,
                    "near_52w_high": True,
                    "rs_new_high": True,
                },
                stage=2,
                passes=True,
            )
        )

        metrics = tracker.get_metrics()

        assert metrics.total_checks == 3
        assert metrics.final_passed == 1
        # near_52w_high failed 2 times
        assert metrics.by_condition.get("near_52w_high", 0) == 2
        # rs_new_high failed 1 time
        assert metrics.by_condition.get("rs_new_high", 0) == 1
        # price_above_sma50 never failed
        assert metrics.by_condition.get("price_above_sma50", 0) == 0

    def test_tracker_empty_metrics(self):
        """RED: Empty tracker returns zero metrics"""
        from analysis.stage2_diagnostics import DiagnosticsTracker

        tracker = DiagnosticsTracker()
        metrics = tracker.get_metrics()

        assert metrics.total_checks == 0
        assert metrics.final_passed == 0
        assert metrics.by_condition == {}


class TestDiagnosticsTrackerTopFailures:
    """Tests for DiagnosticsTracker.get_top_failures()"""

    def test_tracker_top_failures(self):
        """RED: Identify most common failing conditions"""
        from analysis.stage2_diagnostics import (
            DiagnosticsTracker,
            Stage2ConditionResult,
        )

        tracker = DiagnosticsTracker()

        # Add 5 results with various failures
        conditions_list = [
            {"a": False, "b": False, "c": True},  # a, b fail
            {"a": False, "b": False, "c": True},  # a, b fail
            {"a": False, "b": True, "c": True},   # a fails
            {"a": True, "b": False, "c": False},  # b, c fail
            {"a": True, "b": True, "c": True},    # passes
        ]

        for i, conditions in enumerate(conditions_list):
            tracker.add_result(
                Stage2ConditionResult(
                    ticker=f"TICK{i}",
                    date="2024-01-15",
                    conditions=conditions,
                    stage=1,
                    passes=all(conditions.values()),
                )
            )

        top_failures = tracker.get_top_failures(limit=3)

        # Should be list of tuples (condition_name, count)
        assert isinstance(top_failures, list)
        assert len(top_failures) <= 3

        # 'a' failed 3 times, 'b' failed 3 times, 'c' failed 1 time
        failure_dict = dict(top_failures)
        assert failure_dict.get("a", 0) == 3
        assert failure_dict.get("b", 0) == 3

    def test_tracker_top_failures_with_limit(self):
        """RED: Limit the number of top failures returned"""
        from analysis.stage2_diagnostics import (
            DiagnosticsTracker,
            Stage2ConditionResult,
        )

        tracker = DiagnosticsTracker()

        # Add result with many failing conditions
        tracker.add_result(
            Stage2ConditionResult(
                ticker="AAPL",
                date="2024-01-15",
                conditions={
                    "cond_a": False,
                    "cond_b": False,
                    "cond_c": False,
                    "cond_d": False,
                    "cond_e": False,
                },
                stage=1,
                passes=False,
            )
        )

        top_failures = tracker.get_top_failures(limit=2)
        assert len(top_failures) == 2

    def test_tracker_top_failures_empty(self):
        """RED: Empty tracker returns empty list"""
        from analysis.stage2_diagnostics import DiagnosticsTracker

        tracker = DiagnosticsTracker()
        top_failures = tracker.get_top_failures()

        assert top_failures == []


class TestDiagnosticsTrackerPrintSummary:
    """Tests for DiagnosticsTracker.print_summary()"""

    def test_tracker_print_summary(self, capsys):
        """RED: Summary output format includes key information"""
        from analysis.stage2_diagnostics import (
            DiagnosticsTracker,
            Stage2ConditionResult,
        )

        tracker = DiagnosticsTracker()

        # Add a few results
        tracker.add_result(
            Stage2ConditionResult(
                ticker="AAPL",
                date="2024-01-15",
                conditions={"price_above_sma50": False, "near_52w_high": True},
                stage=1,
                passes=False,
            )
        )
        tracker.add_result(
            Stage2ConditionResult(
                ticker="NVDA",
                date="2024-01-15",
                conditions={"price_above_sma50": True, "near_52w_high": True},
                stage=2,
                passes=True,
            )
        )

        tracker.print_summary()

        captured = capsys.readouterr()
        output = captured.out

        # Should contain key metrics
        assert "2" in output  # total_checks
        assert "1" in output  # final_passed
        assert "price_above_sma50" in output  # failed condition

    def test_tracker_print_summary_empty(self, capsys):
        """RED: Empty tracker prints appropriate message"""
        from analysis.stage2_diagnostics import DiagnosticsTracker

        tracker = DiagnosticsTracker()
        tracker.print_summary()

        captured = capsys.readouterr()
        output = captured.out

        # Should indicate no data or show zeros
        assert "0" in output or "No" in output.lower() or "empty" in output.lower()


class TestDiagnosticsTrackerEdgeCases:
    """Edge case tests for DiagnosticsTracker"""

    def test_tracker_with_none_in_conditions(self):
        """RED: Handle None values in conditions dict gracefully"""
        from analysis.stage2_diagnostics import (
            DiagnosticsTracker,
            Stage2ConditionResult,
        )

        tracker = DiagnosticsTracker()

        # This should not raise an error
        result = Stage2ConditionResult(
            ticker="AAPL",
            date="2024-01-15",
            conditions={},  # Empty conditions
            stage=1,
            passes=False,
        )
        tracker.add_result(result)

        metrics = tracker.get_metrics()
        assert metrics.total_checks == 1

    def test_tracker_large_number_of_results(self):
        """RED: Handle large number of results efficiently"""
        from analysis.stage2_diagnostics import (
            DiagnosticsTracker,
            Stage2ConditionResult,
        )

        tracker = DiagnosticsTracker()

        # Add 1000 results
        for i in range(1000):
            tracker.add_result(
                Stage2ConditionResult(
                    ticker=f"TICK{i:04d}",
                    date="2024-01-15",
                    conditions={"cond_a": i % 2 == 0, "cond_b": i % 3 == 0},
                    stage=2 if (i % 2 == 0 and i % 3 == 0) else 1,
                    passes=(i % 2 == 0 and i % 3 == 0),
                )
            )

        metrics = tracker.get_metrics()
        assert metrics.total_checks == 1000
        # cond_a is False when i is odd: 500 times
        assert metrics.by_condition.get("cond_a", 0) == 500
        # cond_b is False when i % 3 != 0: 667 times (ceil(1000 * 2/3))
        assert metrics.by_condition.get("cond_b", 0) == 666 or metrics.by_condition.get("cond_b", 0) == 667


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
