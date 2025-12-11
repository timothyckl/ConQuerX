"""
Retry utility with exponential backoff.

Provides robust retry logic for operations that may fail temporarily.
"""

import time
import random
from typing import Callable, TypeVar

from utils.logger import setup_logger

logger = setup_logger(__name__)

T = TypeVar('T')


def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> T:
    """
    Retry function with exponential backoff and optional jitter.
    
    Args:
        func: Function to retry (must take no arguments)
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay cap in seconds
        jitter: Add random jitter to prevent thundering herd
        
    Returns:
        Result from successful function call
        
    Raises:
        Last exception if all retries exhausted
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                # last attempt failed, raise the exception
                raise
            
            # calculate exponential backoff: base_delay * (2 ^ attempt)
            delay = min(base_delay * (2 ** attempt), max_delay)
            
            # add jitter: random value between 0 and 1 second
            if jitter:
                delay += random.uniform(0, 1)
            
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            time.sleep(delay)
    
    # this should never be reached, but mypy needs it
    raise RuntimeError("Retry logic exhausted without raising exception")
