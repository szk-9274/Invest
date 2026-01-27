"""
Pytest configuration and fixtures
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

import sys
from pathlib import Path

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))


@pytest.fixture
def sample_stock_data():
    """Fixture for sample stock data"""
    days = 300
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    np.random.seed(42)

    base_price = 100
    returns = np.random.normal(0.0005, 0.02, days)
    prices = base_price * np.exp(np.cumsum(returns))

    return pd.DataFrame({
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        'high': prices * (1 + np.random.uniform(0, 0.02, days)),
        'low': prices * (1 - np.random.uniform(0, 0.02, days)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, days)
    }, index=dates)


@pytest.fixture
def sample_benchmark_data():
    """Fixture for sample benchmark data"""
    days = 300
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    np.random.seed(43)

    base_price = 450
    returns = np.random.normal(0.0003, 0.015, days)
    prices = base_price * np.exp(np.cumsum(returns))

    return pd.DataFrame({
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        'high': prices * (1 + np.random.uniform(0, 0.015, days)),
        'low': prices * (1 - np.random.uniform(0, 0.015, days)),
        'close': prices,
        'volume': np.random.randint(50000000, 100000000, days)
    }, index=dates)


@pytest.fixture
def stage_params():
    """Fixture for stage detection parameters"""
    return {
        'sma_periods': [50, 150, 200],
        'min_price_above_52w_low': 1.30,
        'max_distance_from_52w_high': 0.75,
        'min_slope_200_days': 20,
        'rs_min_rating': 70,
        'rs_new_high_required': True,
        'min_volume': 500000
    }


@pytest.fixture
def vcp_params():
    """Fixture for VCP detection parameters"""
    return {
        'base_period_min': 35,
        'base_period_max': 65,
        'contraction_sequence': [0.25, 0.15, 0.08, 0.05],
        'last_contraction_max': 0.10,
        'dryup_vol_ratio': 0.6,
        'breakout_vol_ratio': 1.5,
        'pivot_min_high_52w_ratio': 0.95,
        'pivot_buffer_atr': 0.5
    }


@pytest.fixture
def full_config():
    """Fixture for full configuration"""
    return {
        'data': {
            'source': 'yfinance',
            'min_market_cap': 2000000000,
            'min_price': 5.0,
            'min_volume': 500000,
            'history_period': '2y'
        },
        'benchmark': {
            'symbol': 'SPY'
        },
        'stage': {
            'sma_periods': [50, 150, 200],
            'min_price_above_52w_low': 1.30,
            'max_distance_from_52w_high': 0.75,
            'min_slope_200_days': 20,
            'rs_min_rating': 70,
            'rs_new_high_required': True,
            'min_volume': 500000
        },
        'vcp': {
            'base_period_min': 35,
            'base_period_max': 65,
            'contraction_sequence': [0.25, 0.15, 0.08, 0.05],
            'last_contraction_max': 0.10,
            'dryup_vol_ratio': 0.6,
            'breakout_vol_ratio': 1.5,
            'pivot_min_high_52w_ratio': 0.95,
            'pivot_buffer_atr': 0.5
        },
        'entry': {
            'buy_zone_pct': 0.03,
            'breakout_vol_ratio': 1.5
        },
        'risk': {
            'risk_per_trade': 0.0075,
            'max_loss_hard': 0.10,
            'initial_stop_max': 0.07
        },
        'backtest': {
            'start_date': '2020-01-01',
            'end_date': '2025-01-27',
            'initial_capital': 10000,
            'max_positions': 5,
            'commission': 0.001
        },
        'output': {
            'csv_path': 'output/screening_results.csv',
            'log_path': 'output/screening.log',
            'log_level': 'INFO'
        },
        'performance': {
            'max_workers': 4,
            'request_delay': 0.5,
            'retry_attempts': 3,
            'timeout': 30
        }
    }
