import time
from datetime import datetime
from typing import Any, Callable, Optional

from werkzeug.wrappers import Request as WerkzeugRequest

from tracelite.core.config import TraceliteConfig
from tracelite.core.filters import mask_sensitive, should_exclude
from tracelite.core.models import RequestLog


class TraceliteMiddleware:
    def __init__(self, app: Callable, storage: Any, config: TraceliteConfig) -> None:
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

    def __call__(self, environ: dict, start_response: Callable) -> Any:
        """
        WSGI middleware entry point.

        Args:
            environ: The WSGI environment dictionary.
            start_response: The WSGI start_response callable.

        Returns:
            The response iterable.
        """
        start_time: float = time.time()
        req: WerkzeugRequest = WerkzeugRequest(environ)

        # Skip logging if path is excluded
        if should_exclude(req.path, self.config.exclude_paths):
            return self.app(environ, start_response)

        def custom_start_response(
            status: str, headers: list, exc_info: Optional[Any] = None
        ) -> Callable:
            """
            Custom start_response to capture response metadata and log the request.

            Args:
                status: HTTP status string (e.g., "200 OK").
                headers: List of (header, value) tuples.
                exc_info: Optional exception info.

            Returns:
                The original start_response result.
            """
            response_status: int = int(status.split(" ")[0])
            duration: float = (time.time() - start_time) * 1000  # ms

            log: RequestLog = RequestLog(
                timestamp=datetime.utcnow(),
                method=req.method,
                path=req.path,
                status_code=response_status,
                client_ip=req.remote_addr,
                user_agent=req.headers.get("User-Agent"),
                request_headers=mask_sensitive(
                    dict(req.headers), self.config.mask_keys
                ),
                request_body=req.get_data(as_text=True),
                response_headers=dict(headers),
                response_body=None,  # capturing response body is omitted due to complexity
                duration_ms=duration,
            )
            self.storage.store(log)
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)
