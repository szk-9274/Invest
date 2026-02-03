"""
State Conditions: Historical event conditions for backtesting

This module defines conditions that represent historical states rather than
instantaneous point-in-time conditions. The key example is rs_new_high,
which should be treated as "happened within last N days" rather than
"is true right now".

Key Concepts:
1. State conditions are checked against a window of historical data
2. They are used for universe filtering, NOT daily entry decisions
3. They provide context about a stock's recent behavior
"""
import pandas as pd
from typing import Optional
from loguru import logger


def has_recent_rs_new_high(
    rs_line: pd.Series,
    window: int = 20,
    threshold: float = 0.95
) -> bool:
    """
    Check if RS line made a new high within the last N days.

    This is a "state condition" - it checks for a recent historical event,
    not an instantaneous condition. This makes it more suitable for
    filtering rather than daily entry decisions.

    Args:
        rs_line: RS Line time series
        window: Number of days to look back for new high
        threshold: Minimum ratio to 52-week high (default 0.95 = 95%)

    Returns:
        True if RS line made a new high (>= threshold of 52w high) within window

    Example:
        If rs_line peaked 10 days ago at 95% of its 52-week high,
        and window=20, this returns True.
        If the peak was 30 days ago, this returns False.
    """
    if rs_line is None or len(rs_line) < 252:
        logger.debug("RS line has insufficient data for new high check")
        return False

    rs_clean = rs_line.dropna()
    if len(rs_clean) < 252:
        logger.debug(f"RS line has only {len(rs_clean)} valid data points")
        return False

    # Get 52-week high of RS line
    rs_52w_high = rs_clean.tail(252).max()

    # Check if any day in the window reached near the 52w high
    target_level = rs_52w_high * threshold
    recent_data = rs_clean.tail(window)

    # Check if any value in window meets the threshold
    for value in recent_data:
        if value >= target_level:
            return True

    return False


def get_rs_new_high_date(
    rs_line: pd.Series,
    threshold: float = 0.95
) -> Optional[pd.Timestamp]:
    """
    Get the most recent date when RS line made a new high.

    Args:
        rs_line: RS Line time series
        threshold: Minimum ratio to 52-week high

    Returns:
        Date of most recent new high, or None if never
    """
    if rs_line is None or len(rs_line) < 252:
        return None

    rs_clean = rs_line.dropna()
    if len(rs_clean) < 252:
        return None

    rs_52w_high = rs_clean.tail(252).max()
    target_level = rs_52w_high * threshold

    # Find dates where RS >= target
    high_dates = rs_clean[rs_clean >= target_level].index

    if len(high_dates) == 0:
        return None

    return high_dates[-1]


def days_since_rs_new_high(
    rs_line: pd.Series,
    threshold: float = 0.95
) -> Optional[int]:
    """
    Calculate days since RS line made a new high.

    Args:
        rs_line: RS Line time series
        threshold: Minimum ratio to 52-week high

    Returns:
        Number of trading days since new high, or None if never
    """
    high_date = get_rs_new_high_date(rs_line, threshold)

    if high_date is None:
        return None

    rs_clean = rs_line.dropna()
    current_date = rs_clean.index[-1]

    # Count trading days between high and current
    days = len(rs_clean[(rs_clean.index > high_date) & (rs_clean.index <= current_date)])

    return days
