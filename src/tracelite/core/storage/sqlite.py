import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from tracelite.core.models import RequestLog
from tracelite.core.storage.base import ILoggerStorage


class SQLiteStorage(ILoggerStorage):
    def __init__(self, db_path: str = "tracelite.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute(
                """
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                method TEXT,
                path TEXT,
                query TEXT,
                status_code INTEGER,
                client_ip TEXT,
                user_agent TEXT,
                request_headers TEXT,
                request_body TEXT,
                response_headers TEXT,
                response_body TEXT,
                duration_ms REAL,
                sql_queries TEXT
            )
            """
            )

    def store(self, log: RequestLog) -> None:
        with self.conn:
            self.conn.execute(
                """
            INSERT INTO request_logs (
                timestamp, method, path, query, status_code, client_ip, user_agent,
                request_headers, request_body, response_headers, response_body, duration_ms,
                sql_queries
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    (log.timestamp or datetime.now(timezone.utc)).isoformat(),
                    log.method,
                    log.path,
                    log.query,
                    log.status_code,
                    log.client_ip,
                    log.user_agent,
                    json.dumps(log.request_headers),
                    log.request_body,
                    json.dumps(log.response_headers),
                    log.response_body,
                    log.duration_ms,
                    json.dumps(log.sql_queries) if log.sql_queries else None,
                ),
            )

    def fetch_recent(
        self,
        since_seconds: int = 3600,
        filters: Optional[dict[str, str | int]] = None,
    ):
        query = "SELECT * FROM request_logs WHERE timestamp >= datetime('now', ?)"
        params: list[object] = [f"-{since_seconds} seconds"]

        if filters:
            for key, value in filters.items():
                if key not in ["method", "status_code", "path", "client_ip"]:
                    continue  # 안전하게 허용된 필드만
                query += f" AND {key} = ?"
                params.append(str(value))

        query += " ORDER BY timestamp DESC"
        cursor = self.conn.execute(query, params)
        return cursor.fetchall()

    def fetch_by_path(self, path: str, limit: int = 10):
        cursor = self.conn.execute(
            "SELECT * FROM request_logs WHERE path = ? ORDER BY timestamp DESC LIMIT ?",
            (path, limit),
        )
        return cursor.fetchall()

    def export(self, format: str = "json") -> str:
        with self.conn:
            rows = self.conn.execute("SELECT * FROM request_logs").fetchall()
        if format == "json":
            columns = [
                col[0] for col in self.conn.execute("PRAGMA table_info(request_logs)")
            ]
            return json.dumps([dict(zip(columns, row)) for row in rows], indent=2)
        else:
            raise ValueError("Unsupported export format")
