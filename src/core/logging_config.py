"""
AssureX Claim Engine - Structured Logging Configuration
"""

import json
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects for structured parsing."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include request_id if present
        if hasattr(record, "request_id"):
            log_entry["request_id"] = getattr(record, "request_id")

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = "logs/assurex.log",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure root application logger with console and optional rotating file handlers.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger = logging.getLogger("assurex")
    root_logger.setLevel(numeric_level)

    # Avoid duplicate handlers on re-init
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Formatter selection
    if log_format.lower() == "json":
        formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z")
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s (%(module)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler
    if log_file:
        log_path = Path(log_file).resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=str(log_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    root_logger.propagate = False
    return root_logger


def get_logger(name: str = "assurex") -> logging.Logger:
    """Get named logger child under assurex namespace."""
    if name == "assurex":
        return logging.getLogger("assurex")
    return logging.getLogger(f"assurex.{name}")