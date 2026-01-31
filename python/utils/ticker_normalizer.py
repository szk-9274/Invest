"""
Ticker Normalization Utilities

Filters out invalid ticker formats that cause Yahoo Finance API failures.
This module removes tickers with suffixes that represent:
- Warrants (.W, .WS, .WT) - Not tradable equity securities
- Units (.U, .UN) - SPAC units containing shares + warrants
- Preferred shares (.P, .PR, .PRA, etc.) - Different asset class
- Class shares (.A, .B, .C, .D) - Often not the primary listing

These filters significantly reduce Yahoo Finance API failures by removing
tickers that don't have valid financial data or market cap information.
"""

from typing import List, Optional


# Invalid ticker suffixes to filter out
INVALID_SUFFIXES = [
    '.W', '.WS', '.WT',  # Warrants
    '.U', '.UN',         # Units (SPAC)
    '.P', '.PR', '.PRA', '.PRB', '.PRC', '.PRD',  # Preferred shares
    '.A', '.B', '.C', '.D',  # Class shares (dot notation)
]

# Hyphenated class shares to filter (e.g., BRK-A, BRK-B)
HYPHENATED_CLASS_PATTERNS = ['-A', '-B', '-C', '-D']


def normalize_ticker(ticker: str) -> Optional[str]:
    """
    Normalize a single ticker symbol, filtering out invalid formats.

    Returns None if the ticker should be excluded, otherwise returns the
    normalized ticker string.

    Filters out:
    - Warrants: AAPL.W, MSFT.WS, etc.
    - Units: SPAC.U, XYZ.UN
    - Preferred shares: BAC.P, C.PR, JPM.PRA
    - Class shares with dots: GOOGL.A, FB.B
    - Hyphenated class shares: BRK-A, BRK-B
    - None, empty strings, whitespace

    Args:
        ticker: Ticker symbol to normalize

    Returns:
        Normalized ticker string, or None if ticker should be excluded

    Examples:
        >>> normalize_ticker("AAPL")
        "AAPL"
        >>> normalize_ticker("AAPL.W")
        None
        >>> normalize_ticker("BRK-A")
        None
        >>> normalize_ticker("")
        None
    """
    # Handle None and empty/whitespace strings
    if ticker is None:
        return None

    if isinstance(ticker, str):
        ticker = ticker.strip()
        if not ticker:
            return None
    else:
        return None

    # Convert to uppercase for case-insensitive comparison
    ticker_upper = ticker.upper()

    # Check for invalid suffixes (dot notation)
    for suffix in INVALID_SUFFIXES:
        if ticker_upper.endswith(suffix):
            return None

    # Check for hyphenated class shares (e.g., BRK-A, BRK-B)
    for pattern in HYPHENATED_CLASS_PATTERNS:
        if ticker_upper.endswith(pattern):
            return None

    # Valid ticker - return in uppercase
    return ticker_upper


def normalize_tickers(tickers: List[str]) -> List[str]:
    """
    Normalize a batch of ticker symbols, filtering out invalid formats.

    Returns a new list containing only valid, normalized tickers.
    This function is immutable - it does not modify the input list.

    Args:
        tickers: List of ticker symbols to normalize

    Returns:
        New list containing only valid normalized tickers, preserving order

    Examples:
        >>> normalize_tickers(["AAPL", "MSFT.W", "GOOGL"])
        ["AAPL", "GOOGL"]
        >>> normalize_tickers(["AAPL", "MSFT", "GOOGL"])
        ["AAPL", "MSFT", "GOOGL"]
        >>> normalize_tickers([])
        []
    """
    # Filter and normalize tickers, preserving order
    result = []
    for ticker in tickers:
        normalized = normalize_ticker(ticker)
        if normalized is not None:
            result.append(normalized)

    return result
