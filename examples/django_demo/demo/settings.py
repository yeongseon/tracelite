from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "tracelite-demo-secret"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = ["django.contrib.contenttypes"]

MIDDLEWARE = [
    "tracelite.middleware.django.TraceliteMiddleware",
]

ROOT_URLCONF = "demo.urls"

from tracelite.core.config import TraceliteConfig

TRACELITE_CONFIG = TraceliteConfig(enabled=True)

from tracelite.core.storage.sqlite import SQLiteStorage

TRACELITE_STORAGE = SQLiteStorage("tracelite.db")
