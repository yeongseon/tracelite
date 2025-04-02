import os
from typing import Any, Dict, List, Optional

import tomli
from pydantic import BaseModel


class TraceliteConfig(BaseModel):
    enabled: bool = True
    db_path: str = "tracelite.db"
    exclude_paths: List[str] = ["/static", "/favicon.ico"]
    mask_keys: List[str] = ["password", "token"]
    view_columns: List[str] = [
        "timestamp",
        "client_ip",
        "method",
        "path",
        "status",
        "duration",
    ]


def load_config(app_config: Optional[Dict[str, Any]] = None) -> TraceliteConfig:
    config = TraceliteConfig()

    if os.path.exists("tracelite.toml"):
        with open("tracelite.toml", "rb") as f:
            data = tomli.load(f)
            if "storage" in data:
                config.db_path = data["storage"].get("path", config.db_path)
            if "filter" in data:
                config.exclude_paths = data["filter"].get(
                    "exclude_paths", config.exclude_paths
                )
                config.mask_keys = data["filter"].get("mask_keys", config.mask_keys)
            if "tracelite" in data:
                config.enabled = data["tracelite"].get("enabled", config.enabled)
            if "view" in data:
                config.view_columns = data["view"].get("columns", config.view_columns)

    if app_config:
        config.enabled = app_config.get("TRACELITE_ENABLED", config.enabled)
        config.db_path = app_config.get("TRACELITE_DB_PATH", config.db_path)

    return config
