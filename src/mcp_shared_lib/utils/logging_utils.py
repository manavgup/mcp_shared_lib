"""
Utility functions for logging and event tracking.
"""
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union

def configure_logger(
    logger_name: str,
    log_level: int = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    console: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configure a logger with the specified parameters.
    
    Args:
        logger_name: Name of the logger
        log_level: Logging level (default: logging.INFO)
        log_file: Path to log file (default: None, no file logging)
        console: Whether to log to console (default: True)
        format_string: Custom format string (default: None, uses standard format)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        log_file_path = Path(log_file)
        # Create directory if it doesn't exist
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(
    name: str,
    log_level: int = logging.INFO,
    log_file: Optional[Union[str, Path]] = None
) -> logging.Logger:
    """
    Get a logger with standard configuration.
    
    Args:
        name: Name of the logger (typically __name__)
        log_level: Logging level (default: logging.INFO)
        log_file: Path to log file (default: None, no file logging)
        
    Returns:
        Configured logger
    """
    return configure_logger(name, log_level, log_file)

class ProgressTracker:
    """A simple progress tracker for long-running operations."""
    
    def __init__(self, total: int, description: str = "Progress", log_interval: int = 10):
        """
        Initialize the progress tracker.
        
        Args:
            total: Total number of items to process
            description: Description of the operation
            log_interval: How often to log progress (as a percentage)
        """
        self.total = total
        self.description = description
        self.current = 0
        self.log_interval = log_interval
        self.last_logged_percent = 0
        self.logger = get_logger(f"{__name__}.ProgressTracker")
    
    def update(self, increment: int = 1) -> None:
        """
        Update the progress counter.
        
        Args:
            increment: How much to increment the counter
        """
        self.current += increment
        self._report_progress()
    
    def set_progress(self, current: int) -> None:
        """
        Set the progress counter to a specific value.
        
        Args:
            current: The current progress value
        """
        self.current = current
        self._report_progress()
    
    def _report_progress(self) -> None:
        """Report progress if it's time to do so."""
        if self.total <= 0:
            return
            
        percent_complete = min(100, int((self.current / self.total) * 100))
        
        # Log at specified intervals or at 100%
        if (percent_complete >= self.last_logged_percent + self.log_interval or 
            percent_complete == 100 and self.last_logged_percent < 100):
            self.logger.info(f"{self.description}: {percent_complete}% complete ({self.current}/{self.total})")
            self.last_logged_percent = percent_complete

def log_execution_time(logger: logging.Logger, operation_name: str) -> callable:
    """
    Decorator to log the execution time of a function.
    
    Args:
        logger: Logger to use
        operation_name: Name of the operation for logging
        
    Returns:
        Decorator function
    """
    import time
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Starting {operation_name}...")
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.info(f"Completed {operation_name} in {elapsed_time:.2f} seconds")
                return result
            except Exception as e:
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.error(f"Failed {operation_name} after {elapsed_time:.2f} seconds: {e}")
                raise
                
        return wrapper
    
    return decorator
