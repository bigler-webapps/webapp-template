from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve
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

urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html"), name="spa-entry"),
]
