"""Structured logging configuration."""
import logging
import sys
from app.core.config import settings

def _configure_logging() -> None:
    """Configures the root logger based on environment settings."""
    log_level = logging.DEBUG if settings.ENVIRONMENT.lower() == "development" else logging.INFO
    
    log_format = "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
    
    logging.basicConfig(
        stream=sys.stdout,
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

_configure_logging()

def get_logger(name: str) -> logging.Logger:
    """
    Factory function to get a configured logger instance.
    
    Args:
        name (str): The name of the logger.
        
    Returns:
        logging.Logger: A configured logger instance.
    """
    return logging.getLogger(name)
