import pytest
from flask import Flask, jsonify

from tracelite.core.config import load_config
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.middleware.flask import TraceliteMiddleware


@pytest.fixture
def app():
    app = Flask(__name__)
    config = load_config()
    storage = SQLiteStorage(":memory:")
    app.wsgi_app = TraceliteMiddleware(app.wsgi_app, storage, config)

    @app.route("/ping")
    def ping():
        return jsonify(message="pong")

    app.tracelite_storage = storage  # expose for test
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_flask_middleware_logs_request(client):
    response = client.get("/ping")
    assert response.status_code == 200

    logs = client.application.tracelite_storage.fetch_recent()
    assert len(logs) == 1
    log = logs[0]

    assert isinstance(log[1], str)
    assert log[2] == "GET"  # method
    assert log[3] == "/ping"  # path
    assert log[4] == 200  # status_code
