"""
Logging Configuration - Centralized logging setup for the agent
"""

import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    log_dir: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, uses default location)
        log_dir: Directory for log files (if None, uses project root/logs)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
    
    Returns:
        Configured logger instance
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    
    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file or log_dir specified)
    if log_file or log_dir:
        if log_file:
            log_path = log_file
        else:
            # Default to project root/logs directory
            if log_dir is None:
                # Try to find project root
                current_file = Path(__file__)
                project_root = current_file.parent.parent
                log_dir = project_root / "logs"
            else:
                log_dir = Path(log_dir)
            
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "agent.log"
        
        # Ensure log directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File gets all levels
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Default logging setup - will be initialized on first use
# Users can call setup_logging() with custom parameters to override defaults
_initialized = False

def _ensure_initialized():
    """Ensure logging is initialized (lazy initialization)"""
    global _initialized
    if not _initialized:
        # Check for environment variables
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_dir = os.getenv('LOG_DIR')
        log_file = os.getenv('LOG_FILE')
        
        # Convert string paths to Path objects if provided
        log_dir_path = Path(log_dir) if log_dir else None
        log_file_path = Path(log_file) if log_file else None
        
        # Only enable file logging if explicitly requested or LOG_DIR is set
        enable_file_logging = log_dir is not None or log_file is not None
        
        setup_logging(
            log_level=log_level,
            log_file=log_file_path if enable_file_logging else None,
            log_dir=log_dir_path if enable_file_logging else None
        )
        _initialized = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    _ensure_initialized()
    return logging.getLogger(name)

