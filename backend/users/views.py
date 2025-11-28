from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from django_core_micha.invitations.mixins import InviteActionsMixin  # <- NEU
from .serializers import UserSerializer

import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@ensure_csrf_cookie
def csrf_token_view(request):
    return JsonResponse({"detail": "CSRF cookie set"})


class UserViewSet(InviteActionsMixin, viewsets.ModelViewSet):
    """
    User-API:

    - list/retrieve/update/delete: nur für eingeloggte User
    - current: eigenen User lesen/patchen
    - update_role: Rollenverwaltung
    - invite / invite-link: kommen aus InviteActionsMixin
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[IsAuthenticated],
        url_path="current",
    )
    def current(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="update-role",
    )
    def update_role(self, request, pk=None):
        user = self.get_object()
        new_role = request.data.get("role")
        valid_roles = ["admin", "teacher", "student", "none"]

        if new_role not in valid_roles:
            return Response(
                {"detail": "Invalid role."},
                status=400,
            )

        current = request.user

        if current.is_superuser:
            user.profile.role = new_role
            user.profile.save()
            return Response({"detail": "Role updated successfully."})

        curr_role = getattr(current.profile, "role", "none")
        target_role = getattr(user.profile, "role", "none")

        if curr_role == "admin":
            user.profile.role = new_role
            user.profile.save()
            return Response({"detail": "Role updated successfully."})

        if curr_role == "teacher":
            if target_role in ["none", "student"] and new_role in ["none", "student"]:
                user.profile.role = new_role
                user.profile.save()
                return Response({"detail": "Role updated successfully."})
            return Response(
                {"detail": "Teachers cannot change roles for admin or teacher users."},
                status=403,
            )

        return Response({"detail": "Permission denied."}, status=403)
    
    def _is_admin_or_superuser(self, user) -> bool:
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        role = getattr(getattr(user, "profile", None), "role", "none")
        return role in {"admin", "teacher"}
