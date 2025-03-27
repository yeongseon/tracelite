"""
Tracelite middleware for Django applications.
Logs HTTP requests and responses during local development.
"""

from django.utils.deprecation import MiddlewareMixin
from tracelite.core.models import RequestLog
from tracelite.core.filters import should_exclude, mask_sensitive
from datetime import datetime
import time
from typing import Any

class TraceliteMiddleware(MiddlewareMixin):
    def __init__(self, get_response: Any = None, storage: Any = None, config: Any = None) -> None:
        """
        Initialize Django middleware.

        Args:
            get_response: Django's view handler.
            storage: An object with a `.store()` method.
            config: Tracelite config with enabled flag, filters, etc.
        """
        self.get_response = get_response
        self.storage = storage
        self.config = config

    def __call__(self, request):
        if not self.config or not self.config.enabled:
            return self.get_response(request)

        if should_exclude(request.path, self.config.exclude_paths):
            return self.get_response(request)

        start_time = time.time()
        request_body = request.body
        response = self.get_response(request)
        duration = (time.time() - start_time) * 1000

        log = RequestLog(
            timestamp=datetime.utcnow(),
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            client_ip=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_headers=mask_sensitive(dict(request.headers), self.config.mask_keys),
            request_body=request_body.decode("utf-8", errors="ignore"),
            response_headers=dict(response.items()),
            response_body=None,
            duration_ms=duration,
        )

        self.storage.store(log)
        return response
