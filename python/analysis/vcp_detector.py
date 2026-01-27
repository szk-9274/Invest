"""
VCP (Volatility Contraction Pattern) detection module
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from loguru import logger


class VCPDetector:
    """VCP detection class"""

    def __init__(self, params: Dict):
        """
        Initialize the detector.

        Args:
            params: VCP detection parameters
        """
        self.params = params

    def detect_vcp(self, data: pd.DataFrame) -> Optional[Dict]:
        """
        Detect VCP pattern.

        Args:
            data: Stock data with all indicators

        Returns:
            VCP information dictionary, or None if not found
        """
        # Find base period
        base = self.find_base(data)
        if base is None:
            logger.debug("No valid base found")
            return None

        base_start, base_end = base

        # Extract swing highs and lows
        swings = self.extract_swings(data, base_start, base_end)
        if len(swings) < 4:  # Need at least 2 up-down cycles
            logger.debug("Insufficient swings for VCP")
            return None

        # Check contraction sequence
        contractions = self.check_contraction_sequence(swings)
        if contractions is None:
            logger.debug("No valid contraction sequence")
            return None

        # Check for dryup (volume exhaustion)
        dryup = self.check_dryup(data, base_end)

        # Calculate pivot
        pivot = self.calculate_pivot(data, base_start, base_end)

        # 52-week high check
        high_52w, _ = self._get_52w_high_low(data)
        min_ratio = self.params.get('pivot_min_high_52w_ratio', 0.95)
        if pivot < high_52w * min_ratio:
            logger.debug(f"Pivot {pivot:.2f} too far from 52w high {high_52w:.2f}")
            return None

        # Calculate stop price
        stop = self.calculate_stop_price(data, pivot, base_start, base_end)

        # Entry price (pivot + 1%)
        entry = pivot * 1.01

        # Risk percentage
        risk_pct = (entry - stop) / entry

        return {
            'has_vcp': True,
            'pivot': pivot,
            'base_start': data.index[base_start],
            'base_end': data.index[base_end],
            'base_length': base_end - base_start,
            'contractions': contractions,
            'contraction_count': len(contractions),
            'dryup_confirmed': dryup,
            'entry_price': entry,
            'stop_price': stop,
            'risk_pct': risk_pct
        }

    def find_base(self, data: pd.DataFrame) -> Optional[Tuple[int, int]]:
        """
        Find the base period (35-65 days).

        Returns:
            (start_idx, end_idx) or None
        """
        min_period = self.params.get('base_period_min', 35)
        max_period = self.params.get('base_period_max', 65)

        # Search backwards from most recent data
        for period in range(max_period, min_period - 1, -1):
            if len(data) < period:
                continue

            base_data = data.tail(period)

            # Check base validity
            if self._is_valid_base(base_data):
                start_idx = len(data) - period
                end_idx = len(data) - 1
                return (start_idx, end_idx)

        return None

    def _is_valid_base(self, base_data: pd.DataFrame) -> bool:
        """Check if the base is valid"""
        # Price range calculation
        price_range = (base_data['high'].max() - base_data['low'].min()) / base_data['close'].mean()

        # Range should be appropriate (10-40%)
        if price_range < 0.10 or price_range > 0.40:
            return False

        # Sufficient volume
        if base_data['volume'].mean() < 100_000:
            return False

        return True

    def extract_swings(
        self,
        data: pd.DataFrame,
        base_start: int,
        base_end: int
    ) -> List[Dict]:
        """
        Extract swing highs and lows.

        Returns:
            [{'type': 'high'/'low', 'price': float, 'idx': int}, ...]
        """
        base_data = data.iloc[base_start:base_end + 1].copy()
        swings = []

        # Simple peak/trough detection
        window = 5

        for i in range(window, len(base_data) - window):
            # High detection
            current_high = base_data['high'].iloc[i]
            window_highs = base_data['high'].iloc[i - window:i + window + 1]
            if current_high == window_highs.max():
                swings.append({
                    'type': 'high',
                    'price': current_high,
                    'idx': base_start + i
                })

            # Low detection
            current_low = base_data['low'].iloc[i]
            window_lows = base_data['low'].iloc[i - window:i + window + 1]
            if current_low == window_lows.min():
                swings.append({
                    'type': 'low',
                    'price': current_low,
                    'idx': base_start + i
                })

        # Sort by time
        swings.sort(key=lambda x: x['idx'])

        # Remove consecutive same types
        filtered_swings = []
        for swing in swings:
            if not filtered_swings or filtered_swings[-1]['type'] != swing['type']:
                filtered_swings.append(swing)

        return filtered_swings

    def check_contraction_sequence(self, swings: List[Dict]) -> Optional[List[float]]:
        """
        Check contraction sequence.

        Returns:
            List of contraction percentages, or None if invalid
        """
        # Extract high-low-high pairs
        pullbacks = []

        for i in range(len(swings) - 2):
            if (swings[i]['type'] == 'high' and
                swings[i + 1]['type'] == 'low' and
                swings[i + 2]['type'] == 'high'):

                high1 = swings[i]['price']
                low = swings[i + 1]['price']

                # Pullback percentage calculation
                pullback_pct = (high1 - low) / high1
                pullbacks.append(pullback_pct)

        if len(pullbacks) < 2:
            return None

        # Check contraction pattern (decreasing pullbacks)
        for i in range(len(pullbacks) - 1):
            # Allow some tolerance (next pullback should be at most 90% of previous)
            if pullbacks[i + 1] > pullbacks[i] * 1.1:
                return None  # Not contracting

        # Last contraction should be 10% or less
        last_contraction_max = self.params.get('last_contraction_max', 0.10)
        if pullbacks[-1] > last_contraction_max:
            return None

        return pullbacks

    def check_dryup(self, data: pd.DataFrame, base_end: int) -> bool:
        """
        Check for volume dryup (exhaustion).

        Args:
            data: Stock data
            base_end: Base end index

        Returns:
            True: Dryup confirmed
        """
        if base_end < 50:
            return False

        recent_data = data.iloc[max(0, base_end - 10):base_end + 1]
        vol_ma_10 = recent_data['volume'].mean()

        older_data = data.iloc[max(0, base_end - 50):base_end + 1]
        vol_ma_50 = older_data['volume'].mean()

        if vol_ma_50 == 0:
            return False

        ratio = vol_ma_10 / vol_ma_50

        dryup_ratio = self.params.get('dryup_vol_ratio', 0.6)
        return ratio <= dryup_ratio

    def calculate_pivot(
        self,
        data: pd.DataFrame,
        base_start: int,
        base_end: int
    ) -> float:
        """
        Calculate pivot price (base high).
        """
        base_data = data.iloc[base_start:base_end + 1]
        pivot = base_data['high'].max()
        return pivot

    def calculate_stop_price(
        self,
        data: pd.DataFrame,
        pivot: float,
        base_start: int,
        base_end: int
    ) -> float:
        """
        Calculate initial stop price.
        """
        base_data = data.iloc[base_start:base_end + 1]

        # Option 1: Pivot - 3%
        stop1 = pivot * 0.97

        # Option 2: Last contraction low - ATR buffer
        last_low = base_data.tail(10)['low'].min()

        atr = data.iloc[base_end].get('atr_14', 0)
        if pd.isna(atr):
            atr = 0

        buffer_atr = self.params.get('pivot_buffer_atr', 0.5)
        stop2 = last_low - (buffer_atr * atr)

        # Use the higher stop (lower risk)
        stop_price = max(stop1, stop2)

        return stop_price

    def _get_52w_high_low(self, data: pd.DataFrame) -> Tuple[float, float]:
        """Get 52-week high and low"""
        lookback = min(252, len(data))
        high_52w = data['high'].tail(lookback).max()
        low_52w = data['low'].tail(lookback).min()
        return high_52w, low_52w


def detect_vcp(data: pd.DataFrame, params: Dict) -> Optional[Dict]:
    """
    Quick VCP detection function.

    Args:
        data: Stock data with indicators
        params: VCP detection parameters

    Returns:
        VCP information or None
    """
    detector = VCPDetector(params)
    return detector.detect_vcp(data)
