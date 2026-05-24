from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/", include("django_core_micha.api_urls")),
    path("api/users/", include("users.urls")),
    path("api/utils/", include("utils.urls")),
    path(
        "manifest.json",
        RedirectView.as_view(url="/static/manifest.json", permanent=False),
    ),
]

# Local dev only: serve /static/ and /media/ via Django so contributors don't
# need a separate reverse proxy. In production, Nginx/Traefik MUST be the
# upstream for /media/ — Django's `static.serve` does not enforce
# Content-Disposition headers, which means stored XSS via uploaded HTML/SVG
# if /media/ is publicly reachable. Tracked as S14 / S92 in
# webapp-management/SECURITY_FINDINGS.md.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html"), name="spa-entry"),
]
