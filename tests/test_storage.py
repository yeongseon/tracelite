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
