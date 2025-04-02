"""
Tracelite middleware for Django applications.
Logs HTTP requests and responses during local development.
"""

import time
from datetime import datetime
from typing import Any

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from tracelite.core.filters import mask_sensitive, should_exclude
from tracelite.core.models import RequestLog


class TraceliteMiddleware(MiddlewareMixin):
    def __init__(
        self, get_response: Any = None, storage: Any = None, config: Any = None
    ) -> None:
        """
        Initialize Django middleware.

        If `storage` and `config` are not passed directly, it will try to get them from Django settings.

        Args:
            get_response: Django's view handler.
            storage: Optional. An object with a `.store()` method.
            config: Optional. Tracelite config with enabled flag, filters, etc.
        """
        self.get_response = get_response
        self.storage = storage or getattr(settings, "TRACELITE_STORAGE", None)
        self.config = config or getattr(settings, "TRACELITE_CONFIG", None)

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
            request_headers=mask_sensitive(
                dict(request.headers), self.config.mask_keys
            ),
            request_body=request_body.decode("utf-8", errors="ignore"),
            response_headers=dict(response.items()),
            response_body=None,
            duration_ms=duration,
        )

        self.storage.store(log)
        return response
