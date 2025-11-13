"""
Logging Configuration
Configures loguru for structured logging with custom formatting
"""

import sys
from loguru import logger
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """Configure loguru logging"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with custom format
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler for errors
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # File handler for all logs
    logger.add(
        log_dir / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG" if settings.DEBUG else "INFO",
        rotation="50 MB",
        retention="7 days",
        compression="zip"
    )
    
    logger.info(f"Logging configured - Level: {settings.LOG_LEVEL}")
