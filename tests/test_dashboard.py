import json
from datetime import datetime, timezone

from tracelite.core.models import RequestLog
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.ui.dashboard import _serialize_log_row, get_dashboard_html, get_logs_json


def test_get_dashboard_html_contains_tracelite():
    html = get_dashboard_html()
    assert "Tracelite" in html


def test_get_dashboard_html_contains_doctype():
    html = get_dashboard_html()
    assert "<!DOCTYPE html>" in html


def test_serialize_log_row_13_columns():
    """New schema with query column (13 elements)."""
    row = (
        1,  # id
        "2026-01-01T00:00:00",  # timestamp
        "GET",  # method
        "/api/test",  # path
        "page=1",  # query
        200,  # status_code
        "127.0.0.1",  # client_ip
        "TestAgent/1.0",  # user_agent
        '{"accept": "json"}',  # request_headers
        None,  # request_body
        '{"content-type": "json"}',  # response_headers
        '{"ok": true}',  # response_body
        12.5,  # duration_ms
    )
    result = _serialize_log_row(row)

    assert result["id"] == 1
    assert result["method"] == "GET"
    assert result["path"] == "/api/test"
    assert result["query"] == "page=1"
    assert result["status_code"] == 200
    assert result["client_ip"] == "127.0.0.1"
    assert result["user_agent"] == "TestAgent/1.0"
    assert result["duration_ms"] == 12.5
    assert result["response_body"] == '{"ok": true}'


def test_serialize_log_row_12_columns_old_schema():
    """Old schema without query column (12 elements)."""
    row = (
        1,  # id
        "2026-01-01T00:00:00",  # timestamp
        "POST",  # method
        "/old",  # path
        201,  # status_code
        "10.0.0.1",  # client_ip
        "OldAgent/1.0",  # user_agent
        "{}",  # request_headers
        '{"data": 1}',  # request_body
        "{}",  # response_headers
        '{"created": true}',  # response_body
        5.0,  # duration_ms
    )
    result = _serialize_log_row(row)

    assert result["query"] is None
    assert result["status_code"] == 201
    assert result["method"] == "POST"
    assert result["path"] == "/old"
    assert result["duration_ms"] == 5.0


def test_get_logs_json_with_data():
    storage = SQLiteStorage(":memory:")
    log = RequestLog(
        timestamp=datetime.now(timezone.utc),
        method="GET",
        path="/test",
        status_code=200,
        client_ip="127.0.0.1",
        request_headers={},
        response_headers={},
    )
    storage.store(log)

    result = json.loads(get_logs_json(storage))
    assert len(result) == 1
    assert result[0]["method"] == "GET"
    assert result[0]["path"] == "/test"
    assert result[0]["status_code"] == 200


def test_get_logs_json_empty_storage():
    storage = SQLiteStorage(":memory:")
    result = get_logs_json(storage)
    assert result == "[]"
