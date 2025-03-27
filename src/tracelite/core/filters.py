def should_exclude(path: str, exclude_paths: list) -> bool:
    """Return True if the path should be excluded from logging."""
    return any(path.startswith(p) for p in exclude_paths)


def mask_sensitive(data: dict, keys_to_mask: list, mask: str = "***") -> dict:
    """Return a copy of the data with sensitive keys masked."""
    return {
        k: (mask if k.lower() in [m.lower() for m in keys_to_mask] else v)
        for k, v in data.items()
    }
