# backend/backend/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from users.views import csrf_token_view  # CSRF helper for React

urlpatterns = [
    path("admin/", admin.site.urls),

    # Classic allauth HTML flows (incl. social login)
    path("accounts/", include("allauth.urls")),

    # Headless allauth API (sessions, login, logout, etc.)
    path("api/auth/", include("allauth.headless.urls")),

    # Your own User API (ViewSet mit InviteActionsMixin etc.)
    path("api/users/", include("users.urls")),

    # CSRF endpoint used by the React frontend (CSRF_URL = '/api/csrf/')
    path("api/csrf/", csrf_token_view, name="csrf-token"),
]

# SPA index + catch-all *after* the API routes
urlpatterns += [
    path("invite/<uidb64>/<token>/", TemplateView.as_view(template_name="index.html")),
    path("reset/<uidb64>/<token>/", TemplateView.as_view(template_name="index.html")),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html"), name="spa-fallback"),
]

# Static / media only in DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
