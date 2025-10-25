"""
Logging utilities for the timetable system.
"""

import logging
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from config import LOGGING_CONFIG


def setup_logger(name=None, level=None):
    """Setup logger with file and console handlers."""
    if name is None:
        name = "timetable_solver"
    
    if level is None:
        level = LOGGING_CONFIG['level']
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(LOGGING_CONFIG['format'])
    
    # Create file handler
    log_file = LOGGING_CONFIG['file']
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name=None):
    """Get existing logger or create new one."""
    if name is None:
        name = "timetable_solver"
    
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    
    return logger
