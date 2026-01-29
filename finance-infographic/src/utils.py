import logging
import os
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str = "finance_infographic", level: Optional[int] = None) -> logging.Logger:
    """Configure and return a logger instance.

    Log level can be set via LOG_LEVEL environment variable.
    Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Determine log level from environment or parameter
        if level is None:
            env_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
            level = getattr(logging, env_level, logging.INFO)

        logger.setLevel(level)

    return logger

def get_project_root() -> Path:
    """Return the root directory of the project."""
    # Assuming this file is in src/utils.py, root is parent of src
    return Path(__file__).resolve().parent.parent

def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path

logger = setup_logger()
