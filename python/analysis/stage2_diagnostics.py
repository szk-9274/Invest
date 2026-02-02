"""
Stage2 Diagnostics Module

Phase 1 of Stage2 zero trades fix: Enhanced Diagnostics
Provides per-ticker condition tracking and aggregate funnel metrics
to diagnose why Stage2 screening may return zero trades.

Classes:
    Stage2ConditionResult: Immutable result of Stage2 condition check for a ticker
    Stage2FunnelMetrics: Aggregate metrics showing failure funnel
    DiagnosticsTracker: Tracks and aggregates diagnostic results
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Stage2ConditionResult:
    """
    Immutable result of Stage2 condition check for a single ticker.

    Attributes:
        ticker: Ticker symbol (e.g., "AAPL")
        date: Date of the check (ISO format string)
        conditions: Dictionary mapping condition names to pass/fail boolean
        stage: Detected stage number (1-4)
        passes: Overall pass/fail for Stage2 criteria
    """

    ticker: str
    date: str
    conditions: Dict[str, bool]
    stage: int
    passes: bool


@dataclass
class Stage2FunnelMetrics:
    """
    Aggregate metrics showing the failure funnel for Stage2 screening.

    Attributes:
        total_checks: Total number of tickers checked
        by_condition: Count of failures per condition name
        final_passed: Number of tickers that passed all conditions
    """

    total_checks: int = 0
    by_condition: Dict[str, int] = field(default_factory=dict)
    final_passed: int = 0


class DiagnosticsTracker:
    """
    Tracks Stage2 condition check results and provides aggregate metrics.

    This class collects Stage2ConditionResult objects and computes
    aggregate statistics to help diagnose screening issues.

    Usage:
        tracker = DiagnosticsTracker()
        tracker.add_result(result1)
        tracker.add_result(result2)
        metrics = tracker.get_metrics()
        tracker.print_summary()
    """

    def __init__(self) -> None:
        """Initialize an empty diagnostics tracker."""
        self._results: List[Stage2ConditionResult] = []
        self._failure_counts: Dict[str, int] = {}
        self._passed_count: int = 0

    def add_result(self, result: Stage2ConditionResult) -> None:
        """
        Add a Stage2 condition check result to the tracker.

        This method updates internal counters for efficient metrics retrieval.
        Results are stored immutably.

        Args:
            result: The Stage2ConditionResult to add
        """
        # Store the result (immutable copy via dataclass)
        self._results = [*self._results, result]

        # Update passed count
        if result.passes:
            self._passed_count += 1

        # Update failure counts per condition
        for condition_name, passed in result.conditions.items():
            if not passed:
                current_count = self._failure_counts.get(condition_name, 0)
                # Create new dict to maintain immutability pattern
                self._failure_counts = {
                    **self._failure_counts,
                    condition_name: current_count + 1,
                }

    def get_metrics(self) -> Stage2FunnelMetrics:
        """
        Get aggregate funnel metrics from all tracked results.

        Returns:
            Stage2FunnelMetrics containing total checks, per-condition
            failure counts, and final passed count.
        """
        return Stage2FunnelMetrics(
            total_checks=len(self._results),
            by_condition=dict(self._failure_counts),
            final_passed=self._passed_count,
        )

    def get_top_failures(self, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Get the most common failing conditions.

        Args:
            limit: Maximum number of conditions to return (default 5)

        Returns:
            List of (condition_name, failure_count) tuples, sorted by
            failure count descending.
        """
        if not self._failure_counts:
            return []

        # Sort by failure count descending, then by name for stability
        sorted_failures = sorted(
            self._failure_counts.items(),
            key=lambda x: (-x[1], x[0]),
        )

        return sorted_failures[:limit]

    def print_summary(self) -> None:
        """
        Print a diagnostic summary to stdout.

        Outputs key metrics including total checks, pass rate,
        and top failing conditions.
        """
        metrics = self.get_metrics()

        print("=" * 60)
        print("Stage2 Diagnostics Summary")
        print("=" * 60)

        print(f"Total tickers checked: {metrics.total_checks}")
        print(f"Final passed (Stage2): {metrics.final_passed}")

        if metrics.total_checks > 0:
            pass_rate = (metrics.final_passed / metrics.total_checks) * 100
            print(f"Pass rate: {pass_rate:.1f}%")

        print()
        print("Failure counts by condition:")

        if not metrics.by_condition:
            print("  (No failures recorded)")
        else:
            top_failures = self.get_top_failures(limit=10)
            for condition_name, count in top_failures:
                if metrics.total_checks > 0:
                    pct = (count / metrics.total_checks) * 100
                    print(f"  {condition_name}: {count} ({pct:.1f}%)")
                else:
                    print(f"  {condition_name}: {count}")

        print("=" * 60)
