"""Routes available only in the verified disposable instance."""
from django.urls import include, path
from django.views.static import serve

from .urls import urlpatterns as app_patterns

urlpatterns = [
    path("api/test-management/", include("django_core_micha.test_management.urls")),
    path("static/<path:path>", serve, {"document_root": "/app/frontend_host/build_current/static"}),
    *app_patterns,
]
