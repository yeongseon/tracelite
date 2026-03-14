# pyright: reportMissingImports=false
"""Detect slow API endpoints using Tracelite's slow request highlighting."""

import time
from datetime import datetime, timezone

from fastapi import FastAPI

from tracelite import enable_tracing  # type: ignore[reportMissingImports]
from tracelite.core.config import TraceliteConfig  # type: ignore[reportMissingImports]

app = FastAPI(title="Tracelite Slow Request Example")

# Requests taking longer than this value appear as slow in the dashboard.
config = TraceliteConfig(slow_threshold_ms=300)
enable_tracing(app, config=config)


@app.get("/")
def read_root():
    return {
        "message": "Call /fast and /slow to compare request durations",
        "slow_threshold_ms": config.slow_threshold_ms,
    }


@app.get("/fast")
def fast_endpoint():
    """This endpoint should stay under the configured threshold."""
    time.sleep(0.05)
    return {
        "endpoint": "fast",
        "handled_at": datetime.now(timezone.utc).isoformat(),
        "sleep_seconds": 0.05,
    }


@app.get("/slow")
def slow_endpoint():
    """This endpoint intentionally exceeds the slow threshold."""
    time.sleep(0.65)
    return {
        "endpoint": "slow",
        "handled_at": datetime.now(timezone.utc).isoformat(),
        "sleep_seconds": 0.65,
    }


if __name__ == "__main__":
    import uvicorn

    # Open /_tracelite and call /fast + /slow to see slow highlighting.
    uvicorn.run(
        "examples.performance.slow_requests:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
