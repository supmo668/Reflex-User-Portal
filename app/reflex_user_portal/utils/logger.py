"""Logger configuration for the application."""
import os
import logging
import sys
from typing import Optional

from ...config import LOG_LEVEL

# Create logger
def get_log_level(level_str: str=None) -> int:
    if not level_str:
        return logging.INFO
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return levels.get(level_str.upper(), logging.INFO)

def get_logger(module:str):
    """Get a logger instance for the specified module."""
    LOG_LEVEL = get_log_level(LOG_LEVEL)
    logger = logging.getLogger("reflex_user_portal")
    logger.setLevel(LOG_LEVEL)
    return logger

logger = default_logger = get_logger("reflex_user_portal")

# Create console handler with formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOG_LEVEL)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Optional name for the logger. If not provided, returns root logger.

    Returns:
        A logger instance.
    """
    if name:
        return logging.getLogger(f"reflex_user_portal.{name}")
    return logger
