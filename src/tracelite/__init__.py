"""Tracelite — DevTools for your backend APIs."""

from tracelite.core.config import TraceliteConfig, load_config
from tracelite.core.storage.sqlite import SQLiteStorage

__version__ = "0.5.0"


def enable_tracing(app, config=None, storage=None, db_path=None):
    """Enable Tracelite tracing on a web application.

    Auto-detects the framework (FastAPI, Flask, Django) and applies
    the appropriate middleware.

    Args:
        app: The web application instance (FastAPI, Flask, or Django WSGI app).
        config: Optional TraceliteConfig. Uses load_config() if not provided.
        storage: Optional storage backend. Uses SQLiteStorage if not provided.
        db_path: Optional database path. Overrides config.db_path if provided.

    Returns:
        The app with tracing middleware applied.

    Example:
        from tracelite import enable_tracing
        enable_tracing(app)
    """
    if config is None:
        config = load_config()

    if db_path is not None:
        config.db_path = db_path

    if storage is None:
        storage = SQLiteStorage(db_path=config.db_path)

    app_type = type(app).__name__
    app_module = type(app).__module__ or ""

    # FastAPI / Starlette detection
    if (
        app_module.startswith("fastapi")
        or app_module.startswith("starlette")
        or app_type in ("FastAPI", "Starlette")
    ):
        from tracelite.middleware.fastapi import TraceliteMiddleware
        from tracelite.ui.dashboard import mount_dashboard_starlette

        app.add_middleware(TraceliteMiddleware, storage=storage, config=config)
        mount_dashboard_starlette(app, storage, config.dashboard_path, config=config)
        return app

    # Flask detection
    if app_module.startswith("flask") or app_type == "Flask":
        from tracelite.middleware.flask import TraceliteMiddleware
        from tracelite.ui.dashboard import mount_dashboard_flask

        app.wsgi_app = TraceliteMiddleware(app.wsgi_app, storage, config)
        mount_dashboard_flask(app, storage, config.dashboard_path, config=config)
        return app

    # Django detection — check if it looks like a WSGI application
    if "django" in app_module.lower() or hasattr(app, "urlconf"):
        from tracelite.middleware.flask import TraceliteMiddleware as WSGIMiddleware

        # Django WSGI apps can use the WSGI middleware wrapper
        return WSGIMiddleware(app, storage, config)

    raise TypeError(
        f"Unsupported application type: {app_type}. "
        "Tracelite supports FastAPI, Flask, and Django."
    )
