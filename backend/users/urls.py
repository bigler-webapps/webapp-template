from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    csrf_token_view,
    NonAuthenticatedPasswordResetView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("csrf/", csrf_token_view, name="csrf"),
    path(
        "non_auth_reset/<uidb64>/<token>/",
        NonAuthenticatedPasswordResetView.as_view(),
        name="non-auth-user-reset",
    ),
    path("", include(router.urls)),
]
