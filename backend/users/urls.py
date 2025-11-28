from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_core_micha.invitations.views import NonAuthenticatedPasswordResetView

from .views import csrf_token_view, UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("csrf/", csrf_token_view, name="csrf"),
    # API-Endpunkt, den verifyResetToken / setNewPassword nutzen:
    path(
        "password-reset/<uidb64>/<token>/",
        NonAuthenticatedPasswordResetView.as_view(),
        name="password-reset-api",
    ),
    path("", include(router.urls)),
]
