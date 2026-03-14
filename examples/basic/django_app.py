# pyright: reportMissingImports=false, reportMissingTypeStubs=false
"""Minimal Django app with Tracelite tracing — single-file setup."""

import os
import sys
from datetime import datetime, timezone

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse
from django.urls import path

from tracelite import enable_tracing  # type: ignore[reportMissingImports]
from tracelite.core.config import TraceliteConfig  # type: ignore[reportMissingImports]
from tracelite.core.storage.sqlite import SQLiteStorage  # type: ignore[reportMissingImports]

# Minimal settings in the same file so no project scaffolding is required.
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="tracelite-example-secret",
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["*"],
    )

import django

django.setup()


def index(request):
    return JsonResponse(
        {
            "message": "Django + Tracelite single-file example",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dashboard": "http://127.0.0.1:8000/_tracelite",
        }
    )


def users(request):
    return JsonResponse(
        {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ]
        }
    )


urlpatterns = [
    path("", index),
    path("users/", users),
]

# One-line setup with enable_tracing(app) on Django's WSGI application.
application = get_wsgi_application()
enable_tracing(
    application,
    config=TraceliteConfig(),
    storage=SQLiteStorage("django_traces.db"),
)


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    # Run directly: python examples/basic/django_app.py
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "examples.basic.django_app")
    execute_from_command_line([sys.argv[0], "runserver", "127.0.0.1:8000"])
