import tomli
from pathlib import Path
from typing import List

class AppConfig:
    def __init__(self, db_path: str, exclude_paths: List[str], mask_keys: List[str]):
        self.db_path = db_path
        self.exclude_paths = exclude_paths
        self.mask_keys = mask_keys

def load_config(file_path: str = "tracelite.toml") -> AppConfig:
    config_path = Path(file_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    with config_path.open("rb") as f:
        data = tomli.load(f)

    db_path = data.get("storage", {}).get("path", "tracelite.db")
    exclude_paths = data.get("filter", {}).get("exclude_paths", [])
    mask_keys = data.get("filter", {}).get("mask_keys", [])

    return AppConfig(db_path=db_path, exclude_paths=exclude_paths, mask_keys=mask_keys)