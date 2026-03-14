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

    @app.get("/search")
    async def search(q: str = ""):
        return {"query": q, "results": []}

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


def test_middleware_captures_response_body(app, storage):
    config = load_config()
    app.add_middleware(TraceliteMiddleware, storage=storage, config=config)
    client = TestClient(app)
    response = client.get("/ping")

    assert response.status_code == 200
    logs = storage.fetch_recent()
    assert len(logs) == 1
    # response_body is at index 11 (new schema with query)
    response_body = logs[0][11]
    assert response_body is not None
    assert "pong" in response_body


def test_middleware_captures_query_string(app, storage):
    config = load_config()
    app.add_middleware(TraceliteMiddleware, storage=storage, config=config)
    client = TestClient(app)
    response = client.get("/search?q=tracelite")

    assert response.status_code == 200
    logs = storage.fetch_recent()
    assert len(logs) == 1
    # query is at index 4
    query = logs[0][4]
    assert query is not None
    assert "tracelite" in query
