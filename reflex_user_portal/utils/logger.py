"""Logger configuration for the application."""
import logging
import sys
from typing import Optional

# Create logger
logger = logging.getLogger("reflex_user_portal")
logger.setLevel(logging.INFO)

# Create console handler with formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

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
