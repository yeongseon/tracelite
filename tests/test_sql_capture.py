"""Tests for SQL query capture module."""

from tracelite.core.sql_capture import (
    get_captured_queries,
    record_query,
    start_sql_capture,
    stop_sql_capture,
)


def test_start_and_stop_capture():
    start_sql_capture()
    queries = stop_sql_capture()
    assert queries == []


def test_record_query_in_capture_context():
    start_sql_capture()
    record_query("SELECT * FROM users")
    record_query("INSERT INTO logs VALUES (?)", duration_ms=5.123, params=["test"])
    queries = stop_sql_capture()
    assert len(queries) == 2
    assert queries[0]["query"] == "SELECT * FROM users"
    assert "duration_ms" not in queries[0]
    assert queries[1]["query"] == "INSERT INTO logs VALUES (?)"
    assert queries[1]["duration_ms"] == 5.123
    assert queries[1]["params"] == "['test']"


def test_record_query_outside_context_is_ignored():
    # No start_sql_capture() called — should silently do nothing
    record_query("SELECT 1")
    # No error raised


def test_get_captured_queries_returns_current_state():
    start_sql_capture()
    record_query("SELECT 1")
    current = get_captured_queries()
    assert len(current) == 1
    assert current[0]["query"] == "SELECT 1"
    # Still capturing — stop returns the same
    queries = stop_sql_capture()
    assert len(queries) == 1


def test_stop_capture_resets_context():
    start_sql_capture()
    record_query("SELECT 1")
    stop_sql_capture()
    # After stop, recording should be ignored
    record_query("SELECT 2")
    assert get_captured_queries() == []


def test_record_query_with_duration_only():
    start_sql_capture()
    record_query("SELECT 1", duration_ms=0.5)
    queries = stop_sql_capture()
    assert queries[0]["duration_ms"] == 0.5
    assert "params" not in queries[0]


def test_record_query_rounds_duration():
    start_sql_capture()
    record_query("SELECT 1", duration_ms=1.23456789)
    queries = stop_sql_capture()
    assert queries[0]["duration_ms"] == 1.235
