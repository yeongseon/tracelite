from flask import request
from tracelite.core.models import RequestLog
from tracelite.core.filters import should_exclude, mask_sensitive
from tracelite.core.config import AppConfig
import time
from datetime import datetime

class TraceliteMiddleware:
    def __init__(self, app, storage, config: AppConfig):
        self.app = app
        self.storage = storage
        self.config = config

    def __call__(self, environ, start_response):
        start_time = time.time()
        req = request

        if should_exclude(req.path, self.config.exclude_paths):
            return self.app(environ, start_response)

        def custom_start_response(status, headers, exc_info=None):
            response_status = int(status.split(" ")[0])
            duration = (time.time() - start_time) * 1000
            log = RequestLog(
                timestamp=datetime.utcnow(),
                method=req.method,
                path=req.path,
                status_code=response_status,
                client_ip=req.remote_addr,
                user_agent=req.headers.get("User-Agent"),
                request_headers=mask_sensitive(dict(req.headers), self.config.mask_keys),
                request_body=req.get_data(as_text=True),
                response_headers=dict(headers),
                response_body=None,  # capturing response body is omitted due to complexity
                duration_ms=duration,
            )
            self.storage.store(log)
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)