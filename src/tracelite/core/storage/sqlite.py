import json
import sqlite3
from datetime import datetime
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
                status_code INTEGER,
                client_ip TEXT,
                user_agent TEXT,
                request_headers TEXT,
                request_body TEXT,
                response_headers TEXT,
                response_body TEXT,
                duration_ms REAL
            )
            """
            )

    def store(self, log: RequestLog) -> None:
        with self.conn:
            self.conn.execute(
                """
            INSERT INTO request_logs (
                timestamp, method, path, status_code, client_ip, user_agent,
                request_headers, request_body, response_headers, response_body, duration_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    log.timestamp.isoformat(),
                    log.method,
                    log.path,
                    log.status_code,
                    log.client_ip,
                    log.user_agent,
                    json.dumps(log.request_headers),
                    log.request_body,
                    json.dumps(log.response_headers),
                    log.response_body,
                    log.duration_ms,
                ),
            )

    def fetch_recent(self, since_seconds: int = 3600, filters: Optional[dict] = None):
        query = "SELECT * FROM request_logs WHERE timestamp >= datetime('now', ?)"
        params = [f"-{since_seconds} seconds"]

        if filters:
            for key, value in filters.items():
                if key not in ["method", "status_code", "path", "client_ip"]:
                    continue  # 안전하게 허용된 필드만
                query += f" AND {key} = ?"
                params.append(value)

        query += " ORDER BY timestamp DESC"
        cursor = self.conn.execute(query, params)
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
