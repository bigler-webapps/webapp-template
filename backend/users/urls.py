# backend/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from views_debug import WhoAmI

from .views import csrf_token_view, UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    # nur noch CSRF-Helper + User-Viewset
    path("csrf/", csrf_token_view, name="csrf"),
    path("api/debug/whoami/", WhoAmI.as_view()),
    
    path("", include(router.urls)),
]
