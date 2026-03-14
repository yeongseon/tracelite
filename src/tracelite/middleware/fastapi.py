import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, cast

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from tracelite.core.filters import mask_body, mask_sensitive, should_exclude
from tracelite.core.models import RequestLog
from tracelite.core.sql_capture import (
    get_captured_queries,
    start_sql_capture,
    stop_sql_capture,
)


class TraceliteMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable[..., Any], storage: Any, config: Any) -> None:
        """
        Initialize the middleware with app, storage, and config.

        Args:
            app: The ASGI app instance.
            storage: Object implementing `.store()` method.
            config: Tracelite configuration object.
        """
        super().__init__(app)
        self.storage = storage
        self.config = config

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process each incoming request and log it based on config settings.

        Args:
            request: The incoming HTTP request.
            call_next: The next request handler in the chain.

        Returns:
            The HTTP response returned by downstream handlers.
        """
        config = cast(Any, self.config)
        storage = cast(Any, self.storage)

        if not config.enabled:
            # Skip tracing if disabled in config
            return await call_next(request)

        if should_exclude(str(request.url.path), config.exclude_paths):
            # Skip paths explicitly excluded from logging
            return await call_next(request)

        if config.capture_sql:
            start_sql_capture()

        start_time: float = time.time()
        request_body: bytes = await request.body()
        response: Response = await call_next(request)
        duration: float = (time.time() - start_time) * 1000

        response_body_str: str = ""
        if config.capture_body and hasattr(response, "body_iterator"):
            response_body_chunks: list[bytes] = []
            async for chunk in response.body_iterator:
                if isinstance(chunk, str):
                    response_body_chunks.append(chunk.encode("utf-8"))
                else:
                    response_body_chunks.append(bytes(chunk))
            response_body_bytes = b"".join(response_body_chunks)
            response_body_str = response_body_bytes.decode("utf-8", errors="ignore")

            from starlette.responses import Response as StarletteResponse

            response = StarletteResponse(
                content=response_body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        request_headers: dict[str, object] = {
            str(k): str(v) for k, v in request.headers.items()
        }
        response_headers: dict[str, object] = {
            str(k): str(v) for k, v in response.headers.items()
        }
        masked_request_headers = {
            k: str(v)
            for k, v in mask_sensitive(request_headers, config.mask_keys).items()
        }
        masked_response_headers = {
            k: str(v)
            for k, v in mask_sensitive(response_headers, config.mask_keys).items()
        }

        # Create a log entry based on request and response
        log: RequestLog = RequestLog(
            timestamp=datetime.now(timezone.utc),
            method=request.method,
            path=str(request.url.path),
            query=request.url.query or None,
            status_code=response.status_code,
            client_ip=request.client.host if request.client else "",
            user_agent=request.headers.get("user-agent", ""),
            request_headers=masked_request_headers,
            request_body=(
                mask_body(
                    request_body.decode("utf-8", errors="ignore"),
                    config.mask_keys,
                )
                if config.capture_body
                else None
            ),
            response_headers=masked_response_headers,
            response_body=(
                mask_body(response_body_str, config.mask_keys)
                if config.capture_body
                else None
            ),
            duration_ms=duration,
            sql_queries=stop_sql_capture() if config.capture_sql else [],
        )

        storage.store(log)
        return response
