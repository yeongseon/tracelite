import shutil
import tempfile
import time
from datetime import datetime
from subprocess import PIPE, Popen
from typing import Optional

import pytest
from typer.testing import CliRunner

from tracelite.cli.main import app, parse_filters
from tracelite.core.models import RequestLog
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.ui.viewer import load_logs


@pytest.mark.skipif(
    shutil.which("streamlit") is None, reason="Streamlit is not installed"
)
def test_streamlit_viewer_launch() -> None:
    """Test that the Streamlit viewer launches without error."""
    process = Popen(
        ["streamlit", "run", "src/tracelite/ui/viewer.py"],
        stdout=PIPE,
        stderr=PIPE,
    )
    time.sleep(3)  # Wait for server to start

    assert process.poll() is None  # Process is running

    process.terminate()  # Stop the server


@pytest.fixture
def sample_db_path() -> str:
    """Create a temporary SQLite database with sample log."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name

    storage = SQLiteStorage(db_path)

    log = RequestLog(
        timestamp=datetime.utcnow(),
        method="GET",
        path="/ping",
        status_code=200,
        client_ip="127.0.0.1",
        user_agent="TestAgent",
        request_headers={},
        request_body="",
        response_headers={},
        response_body="",
        duration_ms=10.0,
    )
    storage.store(log)
    return db_path


def test_load_logs(sample_db_path: str) -> None:
    """Test that load_logs() returns stored logs."""
    logs = load_logs(sample_db_path)
    assert len(logs) == 1
    log = logs[0]
    assert log[2] == "GET"  # method
    assert log[3] == "/ping"  # path
    assert log[4] == 200  # status_code


def test_parse_filters():
    """Test that parse_filters() correctly parses filter strings."""
    filters = ["status=500", "method=POST"]
    result = parse_filters(filters)
    assert result == {"status": "500", "method": "POST"}


runner = CliRunner()


@pytest.fixture
def mock_storage(monkeypatch):
    from tracelite.cli import main
    from tracelite.core.storage.sqlite import SQLiteStorage

    class MockStorage(SQLiteStorage):
        def fetch_recent(self, since_seconds=3600, filters=None):
            return [
                (
                    1,
                    "2025-04-02 09:01:23",
                    "GET",
                    "/api/data",
                    200,
                    "127.0.0.1",
                    None,
                    None,
                    None,
                    None,
                    None,
                    12.34,
                ),
                (
                    2,
                    "2025-04-02 09:05:45",
                    "POST",
                    "/api/submit",
                    201,
                    "192.168.1.1",
                    None,
                    None,
                    None,
                    None,
                    None,
                    45.67,
                ),
            ]

    monkeypatch.setattr(main, "storage", MockStorage(":memory:"))


def test_export_json(mock_storage):
    result = runner.invoke(app, ["export", "--format", "json"])
    assert result.exit_code == 0
    assert '"timestamp": "2025-04-02 09:01:23"' in result.stdout
    assert '"method": "GET"' in result.stdout
    assert '"path": "/api/data"' in result.stdout


def test_export_csv(mock_storage):
    result = runner.invoke(app, ["export", "--format", "csv"])
    assert result.exit_code == 0
    assert "timestamp,client_ip,method,path,status,duration" in result.stdout
    assert "2025-04-02 09:01:23,127.0.0.1,GET,/api/data,200,12.34" in result.stdout
