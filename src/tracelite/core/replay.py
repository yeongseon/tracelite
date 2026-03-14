import shlex
from typing import Dict, Optional


def generate_curl(
    method: str,
    path: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[str] = None,
    base_url: str = "http://localhost:8000",
    query: Optional[str] = None,
) -> str:
    """Generate a curl command from a captured request.

    Args:
        method: HTTP method.
        path: Request path.
        headers: Request headers dict.
        body: Request body string.
        base_url: Base URL for the curl command.
        query: Query string (without leading ?).

    Returns:
        A curl command string.
    """
    url = f"{base_url}{path}"
    if query:
        url = f"{url}?{query}"

    parts = ["curl", "-X", method, shlex.quote(url)]

    if headers:
        skip_headers = {"host", "content-length", "transfer-encoding"}
        for key, value in headers.items():
            if key.lower() in skip_headers:
                continue
            parts.append("-H")
            parts.append(shlex.quote(f"{key}: {value}"))

    if body:
        parts.append("-d")
        parts.append(shlex.quote(body))

    return " \\\n  ".join(parts)
