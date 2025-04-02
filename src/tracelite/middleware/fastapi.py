import time
from datetime import datetime
from typing import Any, Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from tracelite.core.filters import mask_sensitive, should_exclude
from tracelite.core.models import RequestLog


class TraceliteMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: Callable[..., Any], storage: object, config: object
    ) -> None:
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
        if not self.config.enabled:
            # Skip tracing if disabled in config
            return await call_next(request)

        if should_exclude(str(request.url.path), self.config.exclude_paths):
            # Skip paths explicitly excluded from logging
            return await call_next(request)

        start_time: float = time.time()
        request_body: bytes = await request.body()
        response: Response = await call_next(request)
        duration: float = (time.time() - start_time) * 1000

        # Create a log entry based on request and response
        log: RequestLog = RequestLog(
            timestamp=datetime.utcnow(),
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            client_ip=request.client.host if request.client else "",
            user_agent=request.headers.get("user-agent", ""),
            request_headers=mask_sensitive(
                dict(request.headers), self.config.mask_keys
            ),
            request_body=request_body.decode("utf-8", errors="ignore"),
            response_headers=dict(response.headers),
            response_body=None,  # Streaming response body capture is non-trivial
            duration_ms=duration,
        )

        self.storage.store(log)
        return response
