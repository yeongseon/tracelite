# pyright: reportMissingImports=false
"""Debug failing API tests using Tracelite inspection."""

from collections.abc import Generator
from typing import Tuple

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tracelite import enable_tracing  # type: ignore[reportMissingImports]
from tracelite.core.storage.sqlite import SQLiteStorage  # type: ignore[reportMissingImports]


def create_app_with_tracing() -> Tuple[FastAPI, SQLiteStorage]:
    # Use in-memory SQLite so each test session starts clean.
    storage = SQLiteStorage(":memory:")
    app = FastAPI(title="Tracelite pytest debugging example")
    enable_tracing(app, storage=storage)

    @app.get("/status")
    def status():
        return {"service": "ok", "version": "0.5.0"}

    @app.get("/items/{item_id}")
    def get_item(item_id: int):
        return {"item_id": item_id, "name": "widget"}

    return app, storage


@pytest.fixture(scope="module")
def traced_client() -> Generator[Tuple[TestClient, SQLiteStorage], None, None]:
    """Fixture pattern: app + tracing storage available to each test."""
    app, storage = create_app_with_tracing()
    with TestClient(app) as client:
        yield client, storage


def test_debug_after_failure(traced_client: Tuple[TestClient, SQLiteStorage]) -> None:
    """Inspect captured request/response data after a failed assertion."""
    client, storage = traced_client

    # Trigger traffic that will be visible in Tracelite logs.
    response = client.get("/status")

    # Simulate a failing expectation and then inspect traces for quick debugging.
    with pytest.raises(AssertionError):
        assert response.json()["service"] == "healthy"

    rows = storage.fetch_recent(since_seconds=3600)
    assert rows, "Expected at least one captured request"

    # SQLite columns in request_logs: path index=3, status_code index=5, response_body index=11.
    latest_row = rows[0]
    assert latest_row[3] == "/status"
    assert latest_row[5] == 200
    assert "ok" in (latest_row[11] or "")


if __name__ == "__main__":
    # Run this single example file as a test module:
    # python examples/testing/pytest_debug.py
    raise SystemExit(pytest.main([__file__, "-q"]))
