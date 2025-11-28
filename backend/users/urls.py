# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet  # your ViewSet using InviteActionsMixin, etc.
# from .views import AccessCodeViewSet  # optional, if AccessCode stays in project

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

# Optional: if AccessCodeViewSet stays in the project instead of the lib
# router.register(r"access-codes", AccessCodeViewSet, basename="access-code")

urlpatterns = [
    path("", include(router.urls)),
]
