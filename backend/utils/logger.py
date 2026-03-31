"""
Structured logging configuration for enterprise-grade operation.
Replaces scattered print() statements with a centralized, configurable logger.
"""
import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure and return the application-wide logger."""
    logger = logging.getLogger("cyberguard")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(module)s:%(funcName)s:%(lineno)d — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Singleton logger instance — import this throughout the app
log = setup_logging()
