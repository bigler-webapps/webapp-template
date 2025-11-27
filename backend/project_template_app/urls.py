from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from users.views import csrf_token_view

urlpatterns = [
    path("admin/", admin.site.urls),

    # Headless-API (hier ist dein React-Frontend dran)
    path("api/auth/", include("allauth.headless.urls")),
    path("api/users/", include("users.urls")),
    path("api/csrf/", csrf_token_view, name="csrf-token"),

    path("", TemplateView.as_view(template_name="index.html"), name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    # WICHTIG: komplette Allauth-URLs, nicht nur socialaccount
    # HEADLESS_ONLY=True sorgt dafür, dass klassische Seiten (account_login etc.)
    # nicht „sichtbar“ sind, aber die Provider-Callbacks (google_callback) verfügbar bleiben.
    path("accounts/", include("allauth.urls")),

    # SPA-Fallback ganz am Schluss
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html"), name="spa-fallback"),
]
