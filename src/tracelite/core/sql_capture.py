"""SQL query capture using contextvars for per-request collection.

Usage:
    from tracelite.core.sql_capture import start_sql_capture, stop_sql_capture, get_captured_queries

    # In middleware (automatic):
    start_sql_capture()
    # ... request handling ...
    queries = stop_sql_capture()

    # Manual recording:
    from tracelite.core.sql_capture import record_query
    record_query("SELECT * FROM users WHERE id=?", duration_ms=12.5, params=["123"])

    # SQLAlchemy integration:
    from tracelite.core.sql_capture import install_sqlalchemy_hooks
    install_sqlalchemy_hooks(engine)
"""

import time
from contextvars import ContextVar
from typing import Any, Dict, List, Optional

# Per-request storage for captured SQL queries
_sql_queries: ContextVar[Optional[List[Dict[str, Any]]]] = ContextVar(
    "tracelite_sql_queries", default=None
)


def start_sql_capture() -> None:
    """Start capturing SQL queries for the current request context."""
    _sql_queries.set([])


def stop_sql_capture() -> List[Dict[str, Any]]:
    """Stop capturing and return collected SQL queries."""
    queries = _sql_queries.get()
    _sql_queries.set(None)
    return queries if queries is not None else []


def get_captured_queries() -> List[Dict[str, Any]]:
    """Get currently captured SQL queries without stopping capture."""
    queries = _sql_queries.get()
    return queries if queries is not None else []


def record_query(
    query: str,
    duration_ms: Optional[float] = None,
    params: Optional[Any] = None,
) -> None:
    """Record a SQL query in the current request context.

    Args:
        query: The SQL query string.
        duration_ms: Query execution time in milliseconds.
        params: Query parameters (will be converted to string).
    """
    queries = _sql_queries.get()
    if queries is None:
        return  # Not in a capture context

    entry: Dict[str, Any] = {"query": query}
    if duration_ms is not None:
        entry["duration_ms"] = round(duration_ms, 3)
    if params is not None:
        entry["params"] = str(params)
    queries.append(entry)


def install_sqlalchemy_hooks(engine: Any) -> None:
    """Install SQLAlchemy event hooks to capture SQL queries.

    Args:
        engine: A SQLAlchemy Engine instance.

    Example:
        from sqlalchemy import create_engine
        from tracelite.core.sql_capture import install_sqlalchemy_hooks

        engine = create_engine("sqlite:///app.db")
        install_sqlalchemy_hooks(engine)
    """
    try:
        from sqlalchemy import event
    except ImportError:
        raise ImportError(
            "SQLAlchemy is required for SQL capture hooks. "
            "Install it with: pip install sqlalchemy"
        )

    @event.listens_for(engine, "before_cursor_execute")
    def _before_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        conn.info.setdefault("tracelite_query_start", time.perf_counter())

    @event.listens_for(engine, "after_cursor_execute")
    def _after_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        start = conn.info.pop("tracelite_query_start", None)
        duration_ms = None
        if start is not None:
            duration_ms = (time.perf_counter() - start) * 1000
        record_query(query=statement, duration_ms=duration_ms, params=parameters)
