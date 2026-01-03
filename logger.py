"""Logging utility for the scraper."""
import logging
from config import LOG_FILE, LOG_LEVEL

def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with file and console handlers."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # File handler
        fh = logging.FileHandler(LOG_FILE)
        fh.setLevel(getattr(logging, LOG_LEVEL))
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, LOG_LEVEL))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger
