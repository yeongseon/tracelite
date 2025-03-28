import tempfile
import time
from datetime import datetime
from subprocess import PIPE, Popen

import pytest

from tracelite.core.models import RequestLog
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.ui.viewer import load_logs


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
