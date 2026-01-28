"""
Stage detection module based on Minervini's Stage Theory
"""
import pandas as pd
from typing import Dict
from loguru import logger


class StageDetector:
    """Stage Theory-based detection class"""

    def __init__(self, params: Dict):
        """
        Initialize the detector.

        Args:
            params: Stage detection parameters
        """
        self.params = params

    def detect_stage(
        self,
        data: pd.DataFrame,
        rs_line: pd.Series = None,
        use_benchmark: bool = True,
    ) -> Dict:
        """
        Detect the current stage of the stock.

        Args:
            data: Stock data with all indicators
            rs_line: RS Line Series (optional; None when benchmark disabled)
            use_benchmark: Whether to require RS condition for Stage 2

        Returns:
            {
                'stage': 2,
                'meets_criteria': True,
                'details': {...}
            }
        """
        # Check Stage 2 conditions
        conditions = self.check_stage2_conditions(data, rs_line, use_benchmark)

        # Check if all conditions are met
        meets_all = all(conditions.values())

        # Determine stage
        if meets_all:
            stage = 2
        elif self._is_stage4(data):
            stage = 4
        elif self._is_stage3(data):
            stage = 3
        else:
            stage = 1

        return {
            'stage': stage,
            'meets_criteria': meets_all,
            'details': conditions
        }

    def check_stage2_conditions(
        self,
        data: pd.DataFrame,
        rs_line: pd.Series = None,
        use_benchmark: bool = True,
    ) -> Dict[str, bool]:
        """
        Check the Stage 2 conditions (Trend Template).

        When use_benchmark is False, the RS new high condition is skipped
        (always True), reducing the criteria to 8 non-benchmark conditions.

        Returns:
            Dictionary of condition results
        """
        if len(data) < 252:
            return {key: False for key in [
                'price_above_sma50', 'sma50_above_sma150', 'sma150_above_sma200',
                'ma200_uptrend', 'above_52w_low', 'near_52w_high',
                'ma50_above_ma150_200', 'rs_new_high', 'sufficient_volume'
            ]}

        latest = data.iloc[-1]

        # 52-week high/low
        high_52w, low_52w = self._get_52w_high_low(data)

        # 200-day MA slope
        ma200_slope = self._calculate_ma200_slope(data)

        # RS condition: skip (always True) when benchmark is disabled
        if use_benchmark and rs_line is not None:
            rs_result = self._check_rs_strength(rs_line)
        else:
            rs_result = True

        conditions = {
            # 1. Close > SMA_50 > SMA_150 > SMA_200
            'price_above_sma50': latest['close'] > latest['sma_50'],
            'sma50_above_sma150': latest['sma_50'] > latest['sma_150'],
            'sma150_above_sma200': latest['sma_150'] > latest['sma_200'],

            # 2. 200-day MA in uptrend
            'ma200_uptrend': ma200_slope > 0,

            # 3. 30% above 52-week low
            'above_52w_low': latest['close'] >= low_52w * self.params['min_price_above_52w_low'],

            # 4. Within 25% of 52-week high
            'near_52w_high': latest['close'] >= high_52w * self.params['max_distance_from_52w_high'],

            # 5. 50-day MA above 150 and 200-day MA
            'ma50_above_ma150_200': (
                latest['sma_50'] > latest['sma_150'] and
                latest['sma_50'] > latest['sma_200']
            ),

            # 6. RS new high (auto-True when benchmark disabled)
            'rs_new_high': rs_result,

            # 7. Sufficient volume
            'sufficient_volume': latest['volume_ma_50'] >= self.params.get('min_volume', 500_000)
        }

        return conditions

    def _get_52w_high_low(self, data: pd.DataFrame) -> tuple:
        """Get 52-week high and low"""
        lookback = min(252, len(data))
        high_52w = data['high'].tail(lookback).max()
        low_52w = data['low'].tail(lookback).min()
        return high_52w, low_52w

    def _calculate_ma200_slope(self, data: pd.DataFrame) -> float:
        """Calculate 200-day MA slope"""
        min_days = self.params.get('min_slope_200_days', 20)

        if len(data) < min_days + 1:
            return 0

        if 'sma_200' not in data.columns:
            return 0

        ma200_current = data['sma_200'].iloc[-1]
        ma200_past = data['sma_200'].iloc[-(min_days + 1)]

        if pd.isna(ma200_current) or pd.isna(ma200_past):
            return 0

        slope = ma200_current - ma200_past
        return slope

    def _check_rs_strength(self, rs_line: pd.Series) -> bool:
        """Check RS strength"""
        if len(rs_line) < 252:
            return False

        rs_line_clean = rs_line.dropna()
        if len(rs_line_clean) < 252:
            return False

        # RS Line making 52-week high
        recent_high = rs_line_clean.tail(252).max()
        current = rs_line_clean.iloc[-1]

        return current >= recent_high * 0.95

    def _is_stage4(self, data: pd.DataFrame) -> bool:
        """Stage 4 (Declining) detection"""
        if len(data) < 200:
            return False

        latest = data.iloc[-1]

        if pd.isna(latest.get('sma_200')):
            return False

        return (
            latest['close'] < latest['sma_200'] and
            self._calculate_ma200_slope(data) < 0
        )

    def _is_stage3(self, data: pd.DataFrame) -> bool:
        """Stage 3 (Topping) detection"""
        if len(data) < 200:
            return False

        latest = data.iloc[-1]

        if pd.isna(latest.get('sma_200')):
            return False

        ma200_slope = self._calculate_ma200_slope(data)

        # 200-day MA is flat (within 1%)
        return abs(ma200_slope) < (latest['sma_200'] * 0.01)


def is_stage2(
    data: pd.DataFrame,
    rs_line: pd.Series = None,
    params: Dict = None,
    use_benchmark: bool = True,
) -> bool:
    """
    Quick Stage 2 check function.

    Args:
        data: Stock data with indicators
        rs_line: RS Line Series (optional)
        params: Stage detection parameters
        use_benchmark: Whether to require RS condition

    Returns:
        True if stock is in Stage 2
    """
    if params is None:
        params = {}
    detector = StageDetector(params)
    result = detector.detect_stage(data, rs_line, use_benchmark=use_benchmark)
    return result['stage'] == 2 and result['meets_criteria']
