"""
Logging configuration for the DeepWiki API.

This module contains the logging setup extracted from
existing logging configuration during the restructure.
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class IgnoreLogChangeDetectedFilter(logging.Filter):
    """Filter to suppress 'Detected file change' messages."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        return "Detected file change in" not in record.getMessage()


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
    max_size_mb: int = 10,
    backup_count: int = 5
) -> None:
    """
    Configure logging for the application with log rotation.
    
    Extracted from existing logging_config.py during restructure.
    
    Args:
        level: Log level (default: INFO)
        format_string: Custom log format string
        log_file: Path to log file
        max_size_mb: Max size in MB before rotating (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
    """
    # Determine log directory and default file path
    base_dir = Path(__file__).parent.parent.parent  # Go up to api/ directory
    log_dir = base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    default_log_file = log_dir / "application.log"
    
    # Get log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Get log file path
    if log_file:
        log_file_path = Path(log_file)
    else:
        log_file_path = default_log_file
    
    # Secure path check: must be inside logs/ directory
    log_dir_resolved = log_dir.resolve()
    resolved_path = log_file_path.resolve()
    if not str(resolved_path).startswith(str(log_dir_resolved) + os.sep):
        raise ValueError(f"Log file path '{log_file_path}' is outside the trusted log directory '{log_dir_resolved}'")
    
    # Ensure parent directories exist
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate max bytes
    max_bytes = max_size_mb * 1024 * 1024
    
    # Configure format
    log_format = format_string or "%(asctime)s - %(levelname)s - %(name)s - %(filename):%(lineno)d - %(message)s"
    
    # Create handlers
    file_handler = RotatingFileHandler(
        resolved_path, 
        maxBytes=max_bytes, 
        backupCount=backup_count, 
        encoding="utf-8"
    )
    console_handler = logging.StreamHandler()
    
    # Set format for both handlers
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add filter to suppress "Detected file change" messages
    file_handler.addFilter(IgnoreLogChangeDetectedFilter())
    console_handler.addFilter(IgnoreLogChangeDetectedFilter())
    
    # Apply logging configuration
    logging.basicConfig(
        level=log_level, 
        handlers=[file_handler, console_handler], 
        force=True
    )
    
    # Log configuration info
    logger = logging.getLogger(__name__)
    logger.debug(
        f"Logging configured: level={level}, "
        f"file={resolved_path}, max_size={max_bytes} bytes, "
        f"backup_count={backup_count}"
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified name."""
    return logging.getLogger(name)


def setup_logging_from_env() -> None:
    """Set up logging using environment variables."""
    level = os.environ.get("LOG_LEVEL", "INFO")
    log_file = os.environ.get("LOG_FILE_PATH")
    
    try:
        max_size_mb = int(os.environ.get("LOG_MAX_SIZE", 10))
    except (TypeError, ValueError):
        max_size_mb = 10
    
    try:
        backup_count = int(os.environ.get("LOG_BACKUP_COUNT", 5))
    except ValueError:
        backup_count = 5
    
    setup_logging(
        level=level,
        log_file=log_file,
        max_size_mb=max_size_mb,
        backup_count=backup_count
    )
