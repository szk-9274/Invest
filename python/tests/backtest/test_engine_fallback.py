"""
Tests for BacktestEngine fallback integration
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestEngineInitialization:
    """Test engine initialization with FallbackManager"""

    def test_engine_initializes_fallback_manager(self):
        """Engine should initialize FallbackManager with config"""
        from backtest.engine import BacktestEngine
        from backtest.fallback_manager import FallbackManager

        config = {
            'performance': {'request_delay': 0.5},
            'stage': {
                'strict': {},
                'relaxed': {},
                'auto_fallback_enabled': True,
                'min_trades_threshold': 1
            },
            'vcp': {},
            'backtest': {'initial_capital': 10000, 'max_positions': 5, 'commission': 0.001},
            'risk': {'risk_per_trade': 0.0075}
        }

        engine = BacktestEngine(config)

        # Should have fallback_manager attribute
        assert hasattr(engine, 'fallback_manager')
        assert isinstance(engine.fallback_manager, FallbackManager)
        assert engine.fallback_manager.current_mode == 'strict'


class TestEngineFallbackLogic:
    """Test engine fallback behavior"""

    @patch('backtest.engine.YahooFinanceFetcher')
    def test_engine_uses_strict_mode_initially(self, mock_fetcher_class):
        """Engine should start in strict mode"""
        from backtest.engine import BacktestEngine

        config = {
            'performance': {'request_delay': 0.5},
            'stage': {
                'strict': {'min_volume': 500000},
                'relaxed': {'min_volume': 300000},
                'auto_fallback_enabled': True,
                'min_trades_threshold': 1
            },
            'vcp': {},
            'backtest': {'initial_capital': 10000, 'max_positions': 5, 'commission': 0.001},
            'risk': {'risk_per_trade': 0.0075}
        }

        engine = BacktestEngine(config)

        assert engine.fallback_manager.get_current_mode() == 'strict'
        assert engine.fallback_manager.fallback_triggered == False

    def test_fallback_manager_configuration_from_config(self):
        """FallbackManager should be configured from config"""
        from backtest.engine import BacktestEngine

        config = {
            'performance': {'request_delay': 0.5},
            'stage': {
                'strict': {},
                'relaxed': {},
                'auto_fallback_enabled': False,  # Custom setting
                'min_trades_threshold': 5         # Custom threshold
            },
            'vcp': {},
            'backtest': {'initial_capital': 10000, 'max_positions': 5, 'commission': 0.001},
            'risk': {'risk_per_trade': 0.0075}
        }

        engine = BacktestEngine(config)

        assert engine.fallback_manager.auto_fallback_enabled == False
        assert engine.fallback_manager.min_trades_threshold == 5
