"""
Tracelite middleware for Django applications.
Logs HTTP requests and responses during local development.
"""

import time
from datetime import datetime, timezone
from typing import Any

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from tracelite.core.filters import mask_body, mask_sensitive, should_exclude
from tracelite.core.models import RequestLog
from tracelite.core.sql_capture import (
    get_captured_queries,
    start_sql_capture,
    stop_sql_capture,
)


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
        super().__init__(get_response)
        self.get_response = get_response
        self.storage = storage or getattr(settings, "TRACELITE_STORAGE", None)
        self.config = config or getattr(settings, "TRACELITE_CONFIG", None)

    def __call__(self, request):
        if not self.config or not self.config.enabled:
            return self.get_response(request)

        if should_exclude(request.path, self.config.exclude_paths):
            return self.get_response(request)

        if self.config.capture_sql:
            start_sql_capture()

        start_time = time.time()
        request_body = request.body
        response = self.get_response(request)
        duration = (time.time() - start_time) * 1000

        response_body_str = ""
        if self.config.capture_body:
            response_body_str = response.content.decode("utf-8", errors="ignore")

        request_headers: dict[str, object] = {
            str(k): str(v) for k, v in request.headers.items()
        }
        masked_request_headers = {
            k: str(v)
            for k, v in mask_sensitive(request_headers, self.config.mask_keys).items()
        }
        response_headers: dict[str, object] = {
            str(k): str(v) for k, v in response.items()
        }
        masked_response_headers = {
            k: str(v)
            for k, v in mask_sensitive(response_headers, self.config.mask_keys).items()
        }

        log = RequestLog(
            timestamp=datetime.now(timezone.utc),
            method=request.method,
            path=request.path,
            query=request.META.get("QUERY_STRING", "") or None,
            status_code=response.status_code,
            client_ip=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_headers=masked_request_headers,
            request_body=(
                mask_body(
                    request_body.decode("utf-8", errors="ignore"),
                    self.config.mask_keys,
                )
                if self.config.capture_body
                else None
            ),
            response_headers=masked_response_headers,
            response_body=(
                mask_body(response_body_str, self.config.mask_keys)
                if self.config.capture_body
                else None
            ),
            duration_ms=duration,
            sql_queries=stop_sql_capture() if self.config.capture_sql else [],
        )

        if self.storage is not None:
            self.storage.store(log)
        return response
