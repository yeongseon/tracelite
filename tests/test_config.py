import os
import shutil
import tempfile

import pytest
import tomli_w

from tracelite.core.config import TraceliteConfig, load_config


def test_default_config():
    config = load_config()
    assert isinstance(config, TraceliteConfig)
    assert config.enabled is True
    assert config.db_path == "tracelite.db"
    assert "/static" in config.exclude_paths


def test_config_from_toml():
    toml_data = {
        "tracelite": {"enabled": False},
        "storage": {"path": "custom.db"},
        "filter": {"exclude_paths": ["/api"], "mask_keys": ["secret"]},
    }
    with tempfile.NamedTemporaryFile(delete=False, suffix=".toml") as tmp:
        tomli_w.dump(toml_data, tmp)
        tmp_path = tmp.name

    shutil.move(tmp_path, "tracelite.toml")
    config = load_config()

    assert config.enabled is False
    assert config.db_path == "custom.db"
    assert config.exclude_paths == ["/api"]
    assert config.mask_keys == ["secret"]

    os.remove("tracelite.toml")


def test_config_from_app_config():
    app_config = {
        "TRACELITE_ENABLED": False,
        "TRACELITE_DB_PATH": "injected.db",
    }
    config = load_config(app_config)
    assert config.enabled is False
    assert config.db_path == "injected.db"


def test_app_config_overrides_toml():
    toml_data = {
        "tracelite": {"enabled": True},
        "storage": {"path": "from_toml.db"},
    }
    with tempfile.NamedTemporaryFile(delete=False, suffix=".toml") as tmp:
        tomli_w.dump(toml_data, tmp)
        tmp_path = tmp.name

    shutil.move(tmp_path, "tracelite.toml")
    app_config = {
        "TRACELITE_ENABLED": False,
        "TRACELITE_DB_PATH": "from_app_config.db",
    }
    config = load_config(app_config)

    assert config.enabled is False
    assert config.db_path == "from_app_config.db"

    os.remove("tracelite.toml")
