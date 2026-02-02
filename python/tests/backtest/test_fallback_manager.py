"""
Tests for FallbackManager (strict/relaxed mode switching)
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backtest.fallback_manager import FallbackManager


class TestFallbackManagerInitialization:
    """Test FallbackManager initialization"""

    def test_initialization_with_defaults(self):
        """FallbackManager should initialize with default values"""
        manager = FallbackManager()

        assert manager.current_mode == 'strict'
        assert manager.fallback_triggered == False
        assert manager.auto_fallback_enabled == True
        assert manager.min_trades_threshold == 1

    def test_initialization_with_custom_params(self):
        """FallbackManager should accept custom parameters"""
        manager = FallbackManager(
            auto_fallback_enabled=False,
            min_trades_threshold=5
        )

        assert manager.current_mode == 'strict'
        assert manager.fallback_triggered == False
        assert manager.auto_fallback_enabled == False
        assert manager.min_trades_threshold == 5


class TestShouldFallback:
    """Test fallback decision logic"""

    def test_should_fallback_when_zero_trades(self):
        """Should fallback when trades_count is below threshold"""
        manager = FallbackManager(auto_fallback_enabled=True, min_trades_threshold=1)

        assert manager.should_fallback(trades_count=0) == True

    def test_should_not_fallback_when_trades_exist(self):
        """Should not fallback when trades_count meets threshold"""
        manager = FallbackManager(auto_fallback_enabled=True, min_trades_threshold=1)

        assert manager.should_fallback(trades_count=5) == False
        assert manager.should_fallback(trades_count=1) == False

    def test_should_not_fallback_when_disabled(self):
        """Should not fallback when auto_fallback_enabled is False"""
        manager = FallbackManager(auto_fallback_enabled=False, min_trades_threshold=1)

        assert manager.should_fallback(trades_count=0) == False

    def test_should_not_fallback_when_already_triggered(self):
        """Should not fallback again if already in relaxed mode"""
        manager = FallbackManager(auto_fallback_enabled=True, min_trades_threshold=1)

        # Trigger fallback
        manager.trigger_fallback()

        # Should not fallback again
        assert manager.should_fallback(trades_count=0) == False

    def test_should_fallback_with_custom_threshold(self):
        """Should respect custom min_trades_threshold"""
        manager = FallbackManager(auto_fallback_enabled=True, min_trades_threshold=5)

        assert manager.should_fallback(trades_count=0) == True
        assert manager.should_fallback(trades_count=3) == True
        assert manager.should_fallback(trades_count=4) == True
        assert manager.should_fallback(trades_count=5) == False
        assert manager.should_fallback(trades_count=10) == False


class TestTriggerFallback:
    """Test fallback triggering"""

    def test_trigger_fallback_changes_mode(self):
        """Triggering fallback should switch to relaxed mode"""
        manager = FallbackManager()

        assert manager.current_mode == 'strict'
        assert manager.fallback_triggered == False

        manager.trigger_fallback()

        assert manager.current_mode == 'relaxed'
        assert manager.fallback_triggered == True

    def test_trigger_fallback_is_idempotent(self):
        """Triggering fallback multiple times should be safe"""
        manager = FallbackManager()

        manager.trigger_fallback()
        assert manager.current_mode == 'relaxed'

        # Trigger again
        manager.trigger_fallback()
        assert manager.current_mode == 'relaxed'  # Still relaxed
        assert manager.fallback_triggered == True


class TestGetCurrentMode:
    """Test current mode retrieval"""

    def test_get_current_mode_returns_strict_initially(self):
        """Initially should return strict mode"""
        manager = FallbackManager()

        assert manager.get_current_mode() == 'strict'

    def test_get_current_mode_returns_relaxed_after_fallback(self):
        """After fallback should return relaxed mode"""
        manager = FallbackManager()
        manager.trigger_fallback()

        assert manager.get_current_mode() == 'relaxed'


class TestResetFallback:
    """Test fallback reset functionality"""

    def test_reset_fallback(self):
        """Reset should restore strict mode"""
        manager = FallbackManager()

        # Trigger fallback
        manager.trigger_fallback()
        assert manager.current_mode == 'relaxed'
        assert manager.fallback_triggered == True

        # Reset
        manager.reset()
        assert manager.current_mode == 'strict'
        assert manager.fallback_triggered == False
