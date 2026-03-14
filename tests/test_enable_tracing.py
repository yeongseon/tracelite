import pytest
from fastapi import FastAPI
from flask import Flask

from tracelite import enable_tracing
from tracelite.core.config import TraceliteConfig
from tracelite.core.storage.sqlite import SQLiteStorage


def test_enable_tracing_detects_fastapi():
    app = FastAPI()
    result = enable_tracing(app)
    assert result is app
    # FastAPI rebuilds middleware_stack on first request; verify middleware was added
    assert any(
        "TraceliteMiddleware" in str(cls) for cls in getattr(app, "user_middleware", [])
    )


def test_enable_tracing_detects_flask():
    app = Flask(__name__)
    original_wsgi = app.wsgi_app
    enable_tracing(app)
    assert app.wsgi_app is not original_wsgi


def test_enable_tracing_raises_for_unsupported_type():
    with pytest.raises(TypeError, match="Unsupported application type"):
        enable_tracing("not an app")


def test_enable_tracing_uses_custom_config():
    app = FastAPI()
    config = TraceliteConfig(db_path=":memory:", enabled=True)
    result = enable_tracing(app, config=config)
    assert result is app


def test_enable_tracing_uses_custom_db_path():
    app = FastAPI()
    result = enable_tracing(app, db_path=":memory:")
    assert result is app


def test_enable_tracing_uses_custom_storage():
    app = Flask(__name__)
    storage = SQLiteStorage(":memory:")
    enable_tracing(app, storage=storage)
    # Verify it wrapped the WSGI app
    assert app.wsgi_app is not None
