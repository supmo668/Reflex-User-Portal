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

# Create console handler with formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(get_log_level(LOG_LEVEL))  # Convert string to int

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Add formatter to console handler
console_handler.setFormatter(formatter)

def get_logger(module:str="reflex_user_portal") -> logging.Logger:
    """Get a logger instance for the specified module."""
    module_logger = logging.getLogger(module)
    module_logger.setLevel(get_log_level(LOG_LEVEL))
    
    # Only add handler if it doesn't already have one to avoid duplicates
    if not module_logger.handlers:
        module_logger.addHandler(console_handler)
        # Prevent propagation to avoid duplicate messages from parent loggers
        module_logger.propagate = False
    
    return module_logger

logger = default_logger = get_logger()
