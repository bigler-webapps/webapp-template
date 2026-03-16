from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django_core_micha.auth.views import PasskeyViewSet

from .views import UserViewSet

router = DefaultRouter()
router.register(r"passkeys", PasskeyViewSet, basename="passkey")
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
