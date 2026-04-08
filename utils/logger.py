"""Custom traceability logger for the War Room system."""

import logging
import sys
from pathlib import Path


def setup_logger(output_dir: Path) -> logging.Logger:
    """Configure logging to both console and trace file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("warroom")
    logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    logger.handlers.clear()

    # File handler - detailed trace log
    file_handler = logging.FileHandler(output_dir / "warroom_trace.log", mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler - info level with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "\033[90m[%(asctime)s]\033[0m %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger
