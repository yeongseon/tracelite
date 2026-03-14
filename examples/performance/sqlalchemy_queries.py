# pyright: reportMissingImports=false
"""Capture SQL queries with SQLAlchemy using Tracelite."""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from sqlalchemy import Column, DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from tracelite import enable_tracing  # type: ignore[reportMissingImports]
from tracelite.core.config import TraceliteConfig  # type: ignore[reportMissingImports]
from tracelite.core.sql_capture import (
    install_sqlalchemy_hooks,
    start_sql_capture,
    stop_sql_capture,
)  # type: ignore[reportMissingImports]

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)

# Hook SQLAlchemy events so Tracelite can capture SQL statements and timings.
install_sqlalchemy_hooks(engine)

app = FastAPI(title="Tracelite SQLAlchemy Query Capture Example")

# capture_sql=True is required for SQL query collection in request traces.
config = TraceliteConfig(capture_sql=True)
enable_tracing(app, config=config)


def seed_data() -> None:
    with SessionLocal() as db:
        existing = db.execute(select(User)).scalars().all()
        if existing:
            return
        db.add_all(
            [
                User(email="alice@example.com", created_at=datetime.now(timezone.utc)),
                User(email="bob@example.com", created_at=datetime.now(timezone.utc)),
            ]
        )
        db.commit()


@app.get("/")
def read_root():
    return {
        "message": "Call /users and /users/{id}, then inspect SQL in /_tracelite",
        "capture_sql": config.capture_sql,
    }


@app.get("/users")
def list_users():
    with SessionLocal() as db:
        users = db.execute(select(User).order_by(User.id)).scalars().all()
        return [
            {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ]


@app.get("/users/{user_id}")
def get_user(user_id: int):
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
        }


@app.get("/manual-capture")
def manual_capture_demo():
    """Optional helper showing direct start/stop SQL capture API usage."""
    start_sql_capture()
    with SessionLocal() as db:
        db.execute(select(User).where(User.email.like("%@example.com"))).scalars().all()
    queries = stop_sql_capture()
    return {"captured_queries": queries, "count": len(queries)}


if __name__ == "__main__":
    import uvicorn

    seed_data()
    # Request traces on /users include SQL under the SQL Queries section.
    uvicorn.run(
        "examples.performance.sqlalchemy_queries:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
