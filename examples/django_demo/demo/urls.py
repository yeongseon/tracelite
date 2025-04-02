from app.views import ping
from django.urls import path

urlpatterns = [
    path("ping/", ping),
]
