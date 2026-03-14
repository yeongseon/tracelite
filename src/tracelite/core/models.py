# models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RequestLog:
    timestamp: datetime
    method: str
    path: str
    query: Optional[str] = None
    status_code: int = 0
    client_ip: str = ""
    user_agent: Optional[str] = None
    request_headers: Dict[str, str] = field(default_factory=dict)
    request_body: Optional[str] = None
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: Optional[str] = None
    duration_ms: Optional[float] = None
    sql_queries: Optional[List[Dict[str, Any]]] = field(default_factory=list)
