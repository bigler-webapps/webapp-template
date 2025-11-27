# backend/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_core.invitations.views import NonAuthenticatedPasswordResetView

from .views_debug import WhoAmI

from .views import csrf_token_view, UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    # nur noch CSRF-Helper + User-Viewset
    path("csrf/", csrf_token_view, name="csrf"),
    path("debug/whoami/", WhoAmI.as_view()), 
    
    path("invite/<uidb64>/<token>/", NonAuthenticatedPasswordResetView.as_view(), name="invite-reset"),
    path("reset/<uidb64>/<token>/", NonAuthenticatedPasswordResetView.as_view(), name="password-reset"),


    path("", include(router.urls)),
]
