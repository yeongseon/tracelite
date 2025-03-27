import django
import pytest
from django.conf import settings
from django.http import JsonResponse
from django.test import Client
from django.urls import path

from tracelite.core.config import load_config
from tracelite.core.storage.sqlite import SQLiteStorage

# --- Configure minimal Django test environment ---
settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    SECRET_KEY="test",
    ALLOWED_HOSTS=["*"],
    MIDDLEWARE=[
        "tracelite.middleware.django.TraceliteMiddleware",
    ],
)
django.setup()


# --- Define a simple view for testing ---
def ping(request):
    return JsonResponse({"message": "pong"})


# --- Define URL patterns ---
urlpatterns = [
    path("ping/", ping),
]


# --- Create pytest client fixture ---
@pytest.fixture
def client() -> Client:
    return Client()


# --- Create config and storage fixture for Tracelite ---
@pytest.fixture
def config_and_storage():
    config = load_config()
    storage = SQLiteStorage(":memory:")
    settings.TRACELITE_CONFIG = config
    settings.TRACELITE_STORAGE = storage
    return config, storage


# --- Main test: ensure Tracelite logs request correctly ---
def test_django_middleware_logs_request(client, config_and_storage):
    config, storage = config_and_storage
    response = client.get("/ping/")
    assert response.status_code == 200

    logs = storage.fetch_recent()
    assert len(logs) == 1
    log = logs[0]

    assert isinstance(log[1], str)
    assert log[2] == "GET"  # method
    assert log[3] == "/ping/"  # path
    assert log[4] == 200  # status code
