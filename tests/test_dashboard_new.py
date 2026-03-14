"""Tests for dashboard new features: curl API, diff API, config API, sql_queries serialization."""

import json
from datetime import datetime, timezone

from tracelite.core.models import RequestLog
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.ui.dashboard import (
    _serialize_log_row,
    get_dashboard_html,
    get_logs_json,
)


def test_serialize_log_row_with_14_elements():
    """Test _serialize_log_row with new 14-column schema (includes sql_queries)."""
    row = (
        1,
        "2025-01-01T00:00:00",
        "GET",
        "/test",
        "page=1",
        200,
        "127.0.0.1",
        "TestAgent",
        '{"content-type": "application/json"}',
        None,
        '{"content-type": "application/json"}',
        '{"ok": true}',
        12.5,
        '[{"query": "SELECT 1", "duration_ms": 1.0}]',
    )
    result = _serialize_log_row(row)
    assert result["id"] == 1
    assert result["query"] == "page=1"
    assert result["status_code"] == 200
    assert result["duration_ms"] == 12.5
    assert len(result["sql_queries"]) == 1
    assert result["sql_queries"][0]["query"] == "SELECT 1"


def test_serialize_log_row_with_14_elements_null_sql():
    """Test _serialize_log_row with 14-column schema but null sql_queries."""
    row = (
        1,
        "2025-01-01T00:00:00",
        "GET",
        "/test",
        None,
        200,
        "127.0.0.1",
        "TestAgent",
        "{}",
        None,
        "{}",
        None,
        5.0,
        None,
    )
    result = _serialize_log_row(row)
    assert result["sql_queries"] == []


def test_serialize_log_row_with_13_elements_no_sql():
    """Test _serialize_log_row with 13-column schema (no sql_queries)."""
    row = (
        1,
        "2025-01-01T00:00:00",
        "GET",
        "/test",
        "page=1",
        200,
        "127.0.0.1",
        "TestAgent",
        "{}",
        None,
        "{}",
        None,
        10.0,
    )
    result = _serialize_log_row(row)
    assert result["query"] == "page=1"
    assert result["duration_ms"] == 10.0
    assert result["sql_queries"] == []


def test_dashboard_html_contains_curl_button():
    html = get_dashboard_html()
    assert "Copy curl" in html


def test_dashboard_html_contains_diff_button():
    html = get_dashboard_html()
    assert "Compare" in html


def test_dashboard_html_contains_slow_request_css():
    html = get_dashboard_html()
    assert ".slow" in html
    assert "slow-icon" in html


def test_dashboard_html_contains_sql_queries_display():
    html = get_dashboard_html()
    assert "SQL Queries" in html
    assert "sql-query" in html


def test_dashboard_html_contains_toast():
    html = get_dashboard_html()
    assert "toast" in html


def test_get_logs_json_includes_sql_queries():
    """Test that get_logs_json includes sql_queries field."""
    storage = SQLiteStorage(":memory:")
    log = RequestLog(
        timestamp=datetime.now(timezone.utc),
        method="GET",
        path="/test",
        status_code=200,
        client_ip="127.0.0.1",
        request_headers={},
        response_headers={},
        sql_queries=[{"query": "SELECT 1", "duration_ms": 1.5}],
    )
    storage.store(log)
    result = json.loads(get_logs_json(storage))
    assert len(result) == 1
    assert result[0]["sql_queries"][0]["query"] == "SELECT 1"


def test_storage_stores_and_retrieves_sql_queries():
    """Test that SQLiteStorage correctly persists and retrieves sql_queries."""
    storage = SQLiteStorage(":memory:")
    log = RequestLog(
        timestamp=datetime.now(timezone.utc),
        method="POST",
        path="/api/users",
        status_code=201,
        client_ip="127.0.0.1",
        request_headers={"content-type": "application/json"},
        request_body='{"name": "Alice"}',
        response_headers={"content-type": "application/json"},
        response_body='{"id": 1, "name": "Alice"}',
        duration_ms=25.0,
        sql_queries=[
            {
                "query": "INSERT INTO users (name) VALUES (?)",
                "duration_ms": 3.2,
                "params": "('Alice',)",
            },
            {
                "query": "SELECT * FROM users WHERE id = ?",
                "duration_ms": 1.1,
                "params": "(1,)",
            },
        ],
    )
    storage.store(log)
    rows = storage.fetch_recent()
    assert len(rows) == 1
    row = rows[0]
    # sql_queries is at index 13
    sql_json = row[13]
    assert sql_json is not None
    queries = json.loads(sql_json)
    assert len(queries) == 2
    assert queries[0]["query"] == "INSERT INTO users (name) VALUES (?)"
    assert queries[1]["duration_ms"] == 1.1
