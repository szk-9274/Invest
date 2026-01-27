"""
Logging configuration module
"""
from loguru import logger
from pathlib import Path
import sys


def setup_logger(log_path: str = "output/screening.log", log_level: str = "INFO"):
    """
    Set up the logger with console and file outputs.

    Args:
        log_path: Path to the log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    # Remove existing handlers
    logger.remove()

    # Console output with color formatting
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    # File output with rotation
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_path,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8"
    )

    return logger


def get_logger():
    """
    Get the configured logger instance.

    Returns:
        Logger instance
    """
    return logger
