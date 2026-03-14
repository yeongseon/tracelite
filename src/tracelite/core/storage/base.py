# base.py
from abc import ABC, abstractmethod

from tracelite.core.models import RequestLog


class ILoggerStorage(ABC):
    @abstractmethod
    def store(self, log: RequestLog) -> None:
        """Store a single request log entry."""
        pass

    @abstractmethod
    def fetch_recent(self, since_seconds: int = 3600) -> list[tuple[object, ...]]:
        """Fetch logs from the last N seconds."""
        pass

    @abstractmethod
    def fetch_by_path(self, path: str, limit: int = 10) -> list[tuple[object, ...]]:
        """Fetch recent logs for a specific endpoint path."""
        pass

    @abstractmethod
    def export(self, format: str = "json") -> str:
        """Export all logs to JSON, CSV, etc."""
        pass
