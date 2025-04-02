from datetime import datetime

from tracelite.core.models import RequestLog
from tracelite.core.storage.sqlite import SQLiteStorage


def test_store_and_fetch():
    db = SQLiteStorage(":memory:")
    log = RequestLog(
        timestamp=datetime.utcnow(),
        method="GET",
        path="/test",
        status_code=200,
        client_ip="127.0.0.1",
        request_headers={"User-Agent": "pytest"},
        response_headers={},
    )
    db.store(log)
    result = db.fetch_recent()
    assert len(result) == 1
    assert result[0][3] == "/test"  # path
    assert result[0][4] == 200  # status_code


def test_fetch_recent_with_filters(tmp_path):
    from datetime import datetime

    from tracelite.core.storage.sqlite import SQLiteStorage

    db_path = tmp_path / "test.db"
    storage = SQLiteStorage(str(db_path))

    # Insert sample data
    log1 = RequestLog(
        timestamp=datetime.now(),
        method="GET",
        path="/api/test",
        status_code=200,
        client_ip="127.0.0.1",
        user_agent=None,
        request_headers={},
        request_body="",
        response_headers={},
        response_body="",
        duration_ms=10.0,
    )

    log2 = RequestLog(
        timestamp=datetime.now(),
        method="POST",
        path="/api/test",
        status_code=500,
        client_ip="192.168.0.1",
        user_agent=None,
        request_headers={},
        request_body="",
        response_headers={},
        response_body="",
        duration_ms=45.0,
    )

    storage.store(log1)
    storage.store(log2)

    # Filter by method
    logs = storage.fetch_recent(filters={"method": "POST"})
    assert len(logs) == 1
    assert logs[0][2] == "POST"

    # Filter by status
    logs = storage.fetch_recent(filters={"status_code": 200})
    assert len(logs) == 1
    assert logs[0][4] == 200
