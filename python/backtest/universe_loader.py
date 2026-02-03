"""
UniverseLoader: Load Stage2 universe for backtest

This module handles loading the Stage2 filtered universe from screening results.
Stage2 is evaluated ONCE at the start of backtest, not daily.

The universe loader provides:
1. Load from screening_results.csv file
2. Load from DataFrame (for testing)
3. Logging of universe size
4. Validation of input data
"""
import pandas as pd
from typing import List, Optional, Set
from pathlib import Path
from loguru import logger


class UniverseLoader:
    """
    Load and manage the Stage2 universe for backtesting.

    The universe is the set of tickers that passed Stage2 screening.
    These tickers form the pool from which backtest can select trades.
    Stage2 conditions (including rs_new_high) are NOT re-evaluated daily.
    """

    def __init__(self, screening_results_path: Optional[Path] = None):
        """
        Initialize UniverseLoader.

        Args:
            screening_results_path: Path to screening_results.csv
        """
        self.screening_results_path = screening_results_path
        self._universe: Set[str] = set()

    def load_from_file(self, path: Optional[Path] = None) -> Set[str]:
        """
        Load universe from screening results CSV file.

        Args:
            path: Path to CSV file (uses stored path if not provided)

        Returns:
            Set of ticker symbols in the universe

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file has invalid format
        """
        file_path = path or self.screening_results_path

        if file_path is None:
            raise ValueError("No screening results path provided")

        if not file_path.exists():
            logger.warning(f"Stage2 results file not found: {file_path}")
            raise FileNotFoundError(f"Screening results not found: {file_path}")

        df = pd.read_csv(file_path)
        return self.load_from_dataframe(df)

    def load_from_dataframe(self, df: pd.DataFrame) -> Set[str]:
        """
        Load universe from DataFrame.

        Args:
            df: DataFrame with screening results

        Returns:
            Set of ticker symbols in the universe
        """
        if df.empty:
            logger.warning("Stage2 results DataFrame is empty")
            self._universe = set()
            logger.info(f"Stage2 Universe loaded: 0 tickers")
            return self._universe

        if 'ticker' not in df.columns:
            raise ValueError("DataFrame must have 'ticker' column")

        self._universe = set(df['ticker'].tolist())

        logger.info(f"Stage2 Universe loaded: {len(self._universe)} tickers")
        logger.info(f"Universe selection complete - Entry evaluation uses EntryCondition only")

        return self._universe

    def get_universe(self) -> Set[str]:
        """
        Get the loaded universe.

        Returns:
            Set of ticker symbols
        """
        return self._universe

    def get_universe_size(self) -> int:
        """
        Get the size of the universe.

        Returns:
            Number of tickers in universe
        """
        return len(self._universe)

    def is_in_universe(self, ticker: str) -> bool:
        """
        Check if a ticker is in the universe.

        Args:
            ticker: Ticker symbol

        Returns:
            True if ticker is in universe
        """
        return ticker in self._universe
