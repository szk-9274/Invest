"""
FallbackManager: Manages strict/relaxed mode fallback logic

Handles automatic switching from strict to relaxed mode when
backtest produces insufficient trades.
"""
from loguru import logger
from typing import Optional


class FallbackManager:
    """
    Manages fallback between strict and relaxed filtering modes.

    The manager tracks the current mode (strict/relaxed) and determines
    when to fallback to relaxed mode based on trade count thresholds.
    """

    def __init__(
        self,
        auto_fallback_enabled: bool = True,
        min_trades_threshold: int = 1
    ):
        """
        Initialize the FallbackManager.

        Args:
            auto_fallback_enabled: Whether to enable automatic fallback
            min_trades_threshold: Minimum trades required before fallback
        """
        self.current_mode: str = 'strict'
        self.fallback_triggered: bool = False
        self.auto_fallback_enabled: bool = auto_fallback_enabled
        self.min_trades_threshold: int = min_trades_threshold

    def should_fallback(self, trades_count: int) -> bool:
        """
        Determine if fallback to relaxed mode is needed.

        Args:
            trades_count: Number of trades produced in current mode

        Returns:
            True if fallback should be triggered
        """
        # Don't fallback if disabled
        if not self.auto_fallback_enabled:
            return False

        # Don't fallback if already triggered
        if self.fallback_triggered:
            return False

        # Fallback if trades below threshold
        return trades_count < self.min_trades_threshold

    def trigger_fallback(self) -> None:
        """
        Trigger fallback to relaxed mode.

        Switches from strict to relaxed mode and logs the event.
        Idempotent - can be called multiple times safely.
        """
        if not self.fallback_triggered:
            logger.warning("[FALLBACK] Switching from STRICT to RELAXED mode...")
            logger.warning("[FALLBACK] Strict mode produced insufficient trades")

        self.current_mode = 'relaxed'
        self.fallback_triggered = True

    def get_current_mode(self) -> str:
        """
        Get the current filtering mode.

        Returns:
            Current mode: 'strict' or 'relaxed'
        """
        return self.current_mode

    def reset(self) -> None:
        """
        Reset fallback state to initial (strict mode).

        Useful for testing or running multiple backtests.
        """
        self.current_mode = 'strict'
        self.fallback_triggered = False
        logger.debug("[FALLBACK] Reset to strict mode")
