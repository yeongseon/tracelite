# src/tracelite/middleware/flask.py
from tracelite.core.models import RequestLog
from tracelite.core.filters import should_exclude, mask_sensitive
from datetime import datetime
import time

class TraceliteMiddleware:
    def __init__(self, app, storage, config):
        self.app = app
        self.storage = storage
        self.config = config

    def __call__(self, environ, start_response):
        start_time = time.time()

        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "")
        client_ip = environ.get("REMOTE_ADDR", "")
        user_agent = environ.get("HTTP_USER_AGENT", "")
        headers = {
            k[5:].replace('_', '-').title(): v
            for k, v in environ.items()
            if k.startswith("HTTP_")
        }
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0) or 0)
            body = environ["wsgi.input"].read(content_length).decode("utf-8") if content_length > 0 else None
        except Exception:
            body = None

        if should_exclude(path, self.config.exclude_paths):
            return self.app(environ, start_response)

        def custom_start_response(status, response_headers, exc_info=None):
            duration = (time.time() - start_time) * 1000
            status_code = int(status.split()[0])

            log = RequestLog(
                timestamp=datetime.utcnow(),
                method=method,
                path=path,
                status_code=status_code,
                client_ip=client_ip,
                user_agent=user_agent,
                request_headers=mask_sensitive(headers, self.config.mask_keys),
                request_body=body,
                response_headers=dict(response_headers),
                response_body=None,
                duration_ms=duration,
            )
            self.storage.store(log)

            return start_response(status, response_headers, exc_info)

        return self.app(environ, custom_start_response)
