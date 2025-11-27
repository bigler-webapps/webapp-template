# backend/project_template_app/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Standard-Allauth HTML-Flows inkl. Social-Login
    path("accounts/", include("allauth.urls")),

    # Deine API:
    path("api/users/", include("users.urls")),
    path("api/auth/", include("allauth.headless.urls")),  # darf bleiben, stört Social nicht
]

# SPA-Index
urlpatterns += [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html"), name="spa-fallback"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
