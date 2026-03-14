import json
from typing import Optional


def should_exclude(path: str, exclude_paths: list[str]) -> bool:
    """Return True if the path should be excluded from logging."""
    return any(path.startswith(p) for p in exclude_paths)


def mask_sensitive(
    data: dict[str, object], keys_to_mask: list[str], mask: str = "***"
) -> dict[str, object]:
    """Return a copy of the data with sensitive keys masked."""
    return {
        k: (mask if k.lower() in [m.lower() for m in keys_to_mask] else v)
        for k, v in data.items()
    }


def mask_body(
    body: Optional[str], keys_to_mask: list[str], mask: str = "***"
) -> Optional[str]:
    """Mask sensitive keys in a JSON body string. Returns original if not valid JSON."""
    if not body:
        return body
    try:
        data = json.loads(body)
        if isinstance(data, dict):
            data = _mask_dict_recursive(data, keys_to_mask, mask)
        return json.dumps(data)
    except (json.JSONDecodeError, TypeError):
        return body


def _mask_dict_recursive(
    data: dict[str, object], keys_to_mask: list[str], mask: str
) -> dict[str, object]:
    """Recursively mask sensitive keys in nested dicts."""
    result = {}
    lower_keys = [k.lower() for k in keys_to_mask]
    for k, v in data.items():
        if k.lower() in lower_keys:
            result[k] = mask
        elif isinstance(v, dict):
            result[k] = _mask_dict_recursive(v, keys_to_mask, mask)
        elif isinstance(v, list):
            result[k] = [
                (
                    _mask_dict_recursive(i, keys_to_mask, mask)
                    if isinstance(i, dict)
                    else i
                )
                for i in v
            ]
        else:
            result[k] = v
    return result
