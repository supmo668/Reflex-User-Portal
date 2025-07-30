"""Logger configuration for the application."""
import logging
import sys
from typing import Optional

from pathlib import Path

from app.config import LOG_LEVEL

LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE_PATH = LOGS_DIR / "app.log"

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

LOG_LEVEL = get_log_level(LOG_LEVEL)


logger = logging.getLogger("reflex_user_portal")
logger.setLevel(LOG_LEVEL)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOG_LEVEL)

# File handler
file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
file_handler.setLevel(LOG_LEVEL)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Optional name for the logger. If not provided, returns root logger.

    Returns:
        A logger instance.
    """
    if name:
        return logging.getLogger(f"app.{name}")
    return logger
