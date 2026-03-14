import time
from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from typing import Any

from werkzeug.wrappers import Request as WerkzeugRequest

from tracelite.core.config import TraceliteConfig
from tracelite.core.filters import mask_body, mask_sensitive, should_exclude
from tracelite.core.models import RequestLog
from tracelite.core.sql_capture import (
    get_captured_queries,
    start_sql_capture,
    stop_sql_capture,
)

WSGIStartResponse = Callable[[str, list[tuple[str, str]], Any | None], Any]
WSGIApp = Callable[[dict[str, Any], WSGIStartResponse], Iterable[bytes]]


class TraceliteMiddleware:
    def __init__(self, app: WSGIApp, storage: Any, config: TraceliteConfig) -> None:
        """
        Initialize the Flask Tracelite middleware.

        Args:
            app: The WSGI application to wrap.
            storage: A storage instance implementing `.store()`.
            config: The Tracelite configuration.
        """
        self.app = app
        self.storage = storage
        self.config = config

    def __call__(
        self, environ: dict[str, Any], start_response: WSGIStartResponse
    ) -> Iterable[bytes]:
        """
        WSGI middleware entry point.

        Args:
            environ: The WSGI environment dictionary.
            start_response: The WSGI start_response callable.

        Returns:
            The response iterable.
        """
        if self.config.capture_sql:
            start_sql_capture()

        start_time: float = time.time()
        req: WerkzeugRequest = WerkzeugRequest(environ)

        # Skip logging if path is excluded
        if should_exclude(req.path, self.config.exclude_paths):
            return self.app(environ, start_response)

        response_status: int = 500
        response_headers: list[tuple[str, str]] = []

        def custom_start_response(
            status: str, headers: list[tuple[str, str]], exc_info: Any | None = None
        ) -> Any:
            """
            Custom start_response to capture response metadata and log the request.

            Args:
                status: HTTP status string (e.g., "200 OK").
                headers: List of (header, value) tuples.
                exc_info: Optional exception info.

            Returns:
                The original start_response result.
            """
            nonlocal response_status, response_headers
            response_status = int(status.split(" ")[0])
            response_headers = headers
            return start_response(status, headers, exc_info)

        original_response = self.app(environ, custom_start_response)
        response_body_parts: list[bytes] = []
        try:
            for data in original_response:
                response_body_parts.append(data)
        finally:
            closer = getattr(original_response, "close", None)
            if callable(closer):
                closer()

        response_body_str = b"".join(response_body_parts).decode(
            "utf-8", errors="ignore"
        )
        duration: float = (time.time() - start_time) * 1000

        request_headers: dict[str, object] = {
            str(k): str(v) for k, v in req.headers.items()
        }
        masked_request_headers = {
            k: str(v)
            for k, v in mask_sensitive(request_headers, self.config.mask_keys).items()
        }
        response_header_map: dict[str, object] = {
            str(k): str(v) for k, v in response_headers
        }
        masked_response_headers = {
            k: str(v)
            for k, v in mask_sensitive(
                response_header_map, self.config.mask_keys
            ).items()
        }

        log: RequestLog = RequestLog(
            timestamp=datetime.now(timezone.utc),
            method=req.method,
            path=req.path,
            query=req.query_string.decode("utf-8") or None,
            status_code=response_status,
            client_ip=req.remote_addr or "",
            user_agent=req.headers.get("User-Agent", ""),
            request_headers=masked_request_headers,
            request_body=(
                mask_body(req.get_data(as_text=True), self.config.mask_keys)
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
        self.storage.store(log)

        return response_body_parts
