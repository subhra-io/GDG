"""Tests for configuration management."""

import pytest
from src.config import settings


def test_settings_loaded():
    """Test that settings are loaded correctly."""
    assert settings is not None
    assert settings.postgres_host is not None
    assert settings.mongodb_host is not None
    assert settings.redis_host is not None


def test_postgres_url_format():
    """Test PostgreSQL URL format."""
    url = settings.postgres_url
    assert url.startswith("postgresql://")
    assert settings.postgres_user in url
    assert settings.postgres_host in url
    assert str(settings.postgres_port) in url
    assert settings.postgres_db in url


def test_mongodb_url_format():
    """Test MongoDB URL format."""
    url = settings.mongodb_url
    assert url.startswith("mongodb://")
    assert settings.mongodb_host in url
    assert str(settings.mongodb_port) in url


def test_redis_url_format():
    """Test Redis URL format."""
    url = settings.redis_url
    assert url.startswith("redis://")
    assert settings.redis_host in url
    assert str(settings.redis_port) in url
    assert str(settings.redis_db) in url


def test_api_configuration():
    """Test API configuration."""
    assert settings.api_host is not None
    assert settings.api_port > 0
    assert isinstance(settings.api_reload, bool)


def test_logging_configuration():
    """Test logging configuration."""
    assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    assert settings.log_format in ["json", "console"]
