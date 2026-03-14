from datetime import datetime, timezone

from tracelite.core.models import RequestLog
from tracelite.core.storage.sqlite import SQLiteStorage


def _make_log(method: str, path: str, status_code: int = 200) -> RequestLog:
    return RequestLog(
        timestamp=datetime.now(timezone.utc),
        method=method,
        path=path,
        status_code=status_code,
        client_ip="127.0.0.1",
        request_headers={},
        response_headers={},
    )


def test_fetch_by_path_returns_matching_entries():
    storage = SQLiteStorage(":memory:")
    storage.store(_make_log("GET", "/api/users"))
    storage.store(_make_log("POST", "/api/items"))
    storage.store(_make_log("GET", "/api/users"))

    results = storage.fetch_by_path("/api/users")
    assert len(results) == 2
    for row in results:
        assert row[3] == "/api/users"


def test_fetch_by_path_respects_limit():
    storage = SQLiteStorage(":memory:")
    for _ in range(5):
        storage.store(_make_log("GET", "/api/data"))

    results = storage.fetch_by_path("/api/data", limit=3)
    assert len(results) == 3


def test_fetch_by_path_returns_empty_for_no_match():
    storage = SQLiteStorage(":memory:")
    storage.store(_make_log("GET", "/api/users"))

    results = storage.fetch_by_path("/api/nonexistent")
    assert len(results) == 0


def test_fetch_by_path_ordered_by_timestamp_desc():
    storage = SQLiteStorage(":memory:")
    storage.store(_make_log("GET", "/api/ordered"))
    storage.store(_make_log("POST", "/api/ordered"))
    storage.store(_make_log("PUT", "/api/ordered"))

    results = storage.fetch_by_path("/api/ordered")
    assert len(results) == 3
    # Timestamps should be descending
    timestamps = [row[1] for row in results]
    assert timestamps == sorted(timestamps, reverse=True)
