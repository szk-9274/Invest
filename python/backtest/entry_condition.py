"""
EntryCondition: Lightweight daily entry conditions for backtest

This module defines entry conditions that are suitable for daily evaluation
during backtesting. Unlike Stage2 conditions (which include rs_new_high),
EntryConditions are designed to be practical for daily trade decisions.

Key Design Principles:
1. NO rs_new_high - this is a state condition, not an entry condition
2. Focus on trend and liquidity conditions
3. Config-driven thresholds (no magic numbers)
4. Clear separation from Stage2 universe selection
"""
import pandas as pd
from typing import Dict, Optional, List
from loguru import logger


class EntryCondition:
    """
    Lightweight entry conditions for daily backtest evaluation.

    Unlike Stage2 (which is evaluated once at backtest start for universe selection),
    EntryCondition is evaluated daily to decide if a trade should be entered.

    EntryCondition does NOT include:
    - rs_new_high (too strict for daily evaluation)
    - 52-week high/low thresholds (already checked in Stage2)

    EntryCondition DOES include:
    - price_above_sma50 (trend condition)
    - sma50_above_sma150 (trend structure)
    - sufficient_volume (liquidity condition)
    """

    # Default thresholds (overridden by config)
    DEFAULT_VOLUME_THRESHOLD = 500_000

    def __init__(
        self,
        config: Optional[Dict] = None,
        mode: str = 'strict'
    ):
        """
        Initialize EntryCondition.

        Args:
            config: Configuration dictionary with entry parameters
            mode: 'strict' or 'relaxed' mode
        """
        if mode not in ['strict', 'relaxed']:
            raise ValueError(f"Invalid mode: {mode}. Must be 'strict' or 'relaxed'")

        self.config = config or {}
        self.mode = mode

        # Extract thresholds from config
        entry_config = self.config.get('entry', {})
        stage_config = self.config.get('stage', {})

        # Get mode-specific thresholds
        mode_config = stage_config.get(mode, {})

        self.volume_threshold = mode_config.get(
            'min_volume',
            entry_config.get('min_volume', self.DEFAULT_VOLUME_THRESHOLD)
        )

        logger.debug(f"EntryCondition initialized: mode={mode}, volume_threshold={self.volume_threshold}")

    def get_condition_names(self) -> List[str]:
        """
        Get list of condition names evaluated by EntryCondition.

        Note: rs_new_high is NOT included as it is a state condition,
        not suitable for daily entry evaluation.

        Returns:
            List of condition names
        """
        conditions = [
            'price_above_sma50',
            'sma50_above_sma150',
            'sufficient_volume'
        ]

        if self.mode == 'strict':
            # Strict mode includes additional stability conditions
            conditions.append('sma50_above_sma200')

        return conditions

    def evaluate(self, data: pd.DataFrame) -> Dict:
        """
        Evaluate entry conditions on the given data.

        Args:
            data: DataFrame with OHLCV data and calculated indicators

        Returns:
            {
                'passed': bool,
                'conditions': {
                    'price_above_sma50': bool,
                    'sma50_above_sma150': bool,
                    'sufficient_volume': bool,
                    ...
                },
                'mode': str
            }
        """
        if len(data) < 50:
            return {
                'passed': False,
                'conditions': {name: False for name in self.get_condition_names()},
                'mode': self.mode,
                'reason': 'insufficient_data'
            }

        latest = data.iloc[-1]

        # Build conditions dict
        conditions = {}

        # Trend conditions
        conditions['price_above_sma50'] = self._check_price_above_sma50(latest)
        conditions['sma50_above_sma150'] = self._check_sma50_above_sma150(latest)

        # Strict mode includes sma50 > sma200
        if self.mode == 'strict':
            conditions['sma50_above_sma200'] = self._check_sma50_above_sma200(latest)

        # Liquidity condition
        conditions['sufficient_volume'] = self._check_sufficient_volume(latest)

        # Determine if all conditions pass
        passed = all(conditions.values())

        return {
            'passed': passed,
            'conditions': conditions,
            'mode': self.mode
        }

    def _check_price_above_sma50(self, latest: pd.Series) -> bool:
        """Check if current price is above SMA 50"""
        if 'sma_50' not in latest or pd.isna(latest['sma_50']):
            return False
        return latest['close'] > latest['sma_50']

    def _check_sma50_above_sma150(self, latest: pd.Series) -> bool:
        """Check if SMA 50 is above SMA 150"""
        if 'sma_50' not in latest or 'sma_150' not in latest:
            return False
        if pd.isna(latest['sma_50']) or pd.isna(latest['sma_150']):
            return False
        return latest['sma_50'] > latest['sma_150']

    def _check_sma50_above_sma200(self, latest: pd.Series) -> bool:
        """Check if SMA 50 is above SMA 200 (strict mode only)"""
        if 'sma_50' not in latest or 'sma_200' not in latest:
            return False
        if pd.isna(latest['sma_50']) or pd.isna(latest['sma_200']):
            return False
        return latest['sma_50'] > latest['sma_200']

    def _check_sufficient_volume(self, latest: pd.Series) -> bool:
        """Check if volume meets threshold"""
        if 'volume_ma_50' not in latest:
            # Fall back to raw volume
            if 'volume' not in latest:
                return False
            return latest['volume'] >= self.volume_threshold

        if pd.isna(latest['volume_ma_50']):
            return False

        return latest['volume_ma_50'] >= self.volume_threshold
