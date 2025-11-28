# backend/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Classic allauth HTML flows (optional, for /accounts/*)
    path("accounts/", include("allauth.urls")),
    path("api/", include("django_core_micha.api_urls")),

    # Project-specific user API (ViewSet with InviteActionsMixin etc.)
    path("api/users/", include("users.urls")),
]

# Single Page Application: everything else goes to React's index.html
urlpatterns += [
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html"), name="spa-entry"),
]

# Static/media for local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
