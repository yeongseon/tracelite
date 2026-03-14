import json
from typing import Any, Dict, List, Optional


def diff_responses(
    old_body: Optional[str], new_body: Optional[str]
) -> List[Dict[str, Any]]:
    """Compare two response bodies and return a list of differences.

    Args:
        old_body: Previous response body (JSON string).
        new_body: Current response body (JSON string).

    Returns:
        List of dicts with keys: path, old_value, new_value.
    """
    if old_body is None and new_body is None:
        return []

    old_data = _parse_json(old_body)
    new_data = _parse_json(new_body)

    if old_data is None or new_data is None:
        if old_body != new_body:
            return [{"path": "$", "old_value": old_body, "new_value": new_body}]
        return []

    diffs: List[Dict[str, Any]] = []
    _compare("$", old_data, new_data, diffs)
    return diffs


def diff_responses_text(old_body: Optional[str], new_body: Optional[str]) -> str:
    """Return a human-readable diff string."""
    diffs = diff_responses(old_body, new_body)
    if not diffs:
        return "No differences found."

    lines = []
    for d in diffs:
        lines.append(f"  {d['path']}:")
        lines.append(f"    - {d['old_value']}")
        lines.append(f"    + {d['new_value']}")
    return "\n".join(lines)


def _parse_json(text: Optional[str]) -> Optional[Any]:
    if text is None:
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def _compare(path: str, old: Any, new: Any, diffs: List[Dict[str, Any]]) -> None:
    if type(old) != type(new):
        diffs.append({"path": path, "old_value": old, "new_value": new})
        return

    if isinstance(old, dict):
        all_keys = set(old.keys()) | set(new.keys())
        for key in sorted(all_keys):
            child_path = f"{path}.{key}"
            if key not in old:
                diffs.append(
                    {"path": child_path, "old_value": None, "new_value": new[key]}
                )
            elif key not in new:
                diffs.append(
                    {"path": child_path, "old_value": old[key], "new_value": None}
                )
            else:
                _compare(child_path, old[key], new[key], diffs)
    elif isinstance(old, list):
        max_len = max(len(old), len(new))
        for i in range(max_len):
            child_path = f"{path}[{i}]"
            if i >= len(old):
                diffs.append(
                    {"path": child_path, "old_value": None, "new_value": new[i]}
                )
            elif i >= len(new):
                diffs.append(
                    {"path": child_path, "old_value": old[i], "new_value": None}
                )
            else:
                _compare(child_path, old[i], new[i], diffs)
    else:
        if old != new:
            diffs.append({"path": path, "old_value": old, "new_value": new})
