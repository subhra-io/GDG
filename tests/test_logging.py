"""Tests for logging infrastructure."""

import pytest
from src.core.logging import setup_logging, get_logger


def test_setup_logging():
    """Test logging setup."""
    setup_logging()
    logger = get_logger(__name__)
    assert logger is not None


def test_get_logger():
    """Test logger retrieval."""
    logger = get_logger("test_module")
    assert logger is not None
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")
    assert hasattr(logger, "warning")
    assert hasattr(logger, "debug")


def test_logger_methods():
    """Test logger methods work without errors."""
    logger = get_logger("test_logger")
    
    # These should not raise exceptions
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    logger.debug("Test debug message")
