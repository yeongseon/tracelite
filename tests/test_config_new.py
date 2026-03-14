"""Tests for slow request threshold configuration."""

from tracelite.core.config import TraceliteConfig, load_config


def test_config_has_slow_threshold_ms_default():
    config = TraceliteConfig()
    assert config.slow_threshold_ms == 1000


def test_config_slow_threshold_ms_custom():
    config = TraceliteConfig(slow_threshold_ms=500)
    assert config.slow_threshold_ms == 500


def test_config_has_capture_sql_default():
    config = TraceliteConfig()
    assert config.capture_sql is False


def test_config_capture_sql_enabled():
    config = TraceliteConfig(capture_sql=True)
    assert config.capture_sql is True
