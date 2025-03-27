import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tracelite.core.config import load_config
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.middleware.fastapi import TraceliteMiddleware


@pytest.fixture
def app():
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"message": "pong"}

    return app


@pytest.fixture
def storage():
    return SQLiteStorage(":memory:")


def test_middleware_logs_request(app, storage):
    config = load_config()
    app.add_middleware(TraceliteMiddleware, storage=storage, config=config)
    client = TestClient(app)
    response = client.get("/ping")

    assert response.status_code == 200
    logs = storage.fetch_recent()
    assert len(logs) == 1
    assert "/ping" in logs[0]


def test_middleware_disabled(app, storage):
    config = load_config()
    config.enabled = False
    app.add_middleware(TraceliteMiddleware, storage=storage, config=config)
    client = TestClient(app)
    response = client.get("/ping")

    assert response.status_code == 200
    logs = storage.fetch_recent()
    assert len(logs) == 0
