"""
Logging setup for ConQuerX pipeline.

Provides colour-coded console logging and detailed file logging.
"""

import logging
import sys
from typing import Optional


# colour codes for console output
class LogColours:
    """ANSI colour codes for terminal output."""
    GREY = "\033[90m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"


class ColouredFormatter(logging.Formatter):
    """Custom formatter with colour-coded log levels."""
    
    COLOURS = {
        logging.DEBUG: LogColours.GREY,
        logging.INFO: LogColours.BLUE,
        logging.WARNING: LogColours.YELLOW,
        logging.ERROR: LogColours.RED,
        logging.CRITICAL: LogColours.RED,
    }
    
    def format(self, record):
        # add colour to level name
        levelname = record.levelname
        if record.levelno in self.COLOURS:
            levelname_colour = (
                f"{self.COLOURS[record.levelno]}{levelname}{LogColours.RESET}"
            )
            record.levelname = levelname_colour
        
        return super().format(record)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    verbose: bool = False
) -> logging.Logger:
    """
    Setup logger with console and optional file handlers.
    
    Console handler uses colour-coded levels and simple format.
    File handler uses detailed format with timestamps.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        log_file: Path to log file (default: pipeline.log)
        verbose: If True, set console to DEBUG level, else INFO
        
    Returns:
        Configured logger instance
    """
    # get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # capture all levels
    
    # avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # console handler with colour formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_level = logging.DEBUG if verbose else logging.INFO
    console_handler.setLevel(console_level)
    
    console_format = "[%(asctime)s] [%(levelname)s] %(message)s"
    console_formatter = ColouredFormatter(
        console_format,
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # file handler with detailed formatting (if log_file specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # capture all levels in file
        
        file_format = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        file_formatter = logging.Formatter(
            file_format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # prevent propagation to root logger
    logger.propagate = False
    
    return logger
