# base.py
from abc import ABC, abstractmethod

from tracelite.core.models import RequestLog


class ILoggerStorage(ABC):
    @abstractmethod
    def store(self, log: RequestLog) -> None:
        """Store a single request log entry."""
        pass

    @abstractmethod
    def fetch_recent(self, since_seconds: int = 3600) -> list:
        """Fetch logs from the last N seconds."""
        pass

    @abstractmethod
    def export(self, format: str = "json") -> str:
        """Export all logs to JSON, CSV, etc."""
        pass
