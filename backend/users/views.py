# backend/users/views.py
from django.contrib.auth.models import User

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from .serializers import UserSerializer

import logging

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def csrf_token_view(request):
    """
    Return a simple JSON to ensure CSRF cookie is set on the client.

    Das bleibt praktisch, damit das React-Frontend vor dem ersten POST
    sicher einen CSRF-Cookie bekommt.
    """
    return JsonResponse({"detail": "CSRF cookie set"})


class UserViewSet(viewsets.ModelViewSet):
    """
    User-API ohne eigene Auth-Implementierung.

    - List/Retrieve/Update/Delete: nur für authentifizierte Nutzer (und
      in der Praxis solltest du hier ggf. auf Admins beschränken).
    - `current`: aktuellen User lesen / updaten.
    - `update_role`: Rollenverwaltung mit einfachen Checks.
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
        """
        Return or update the current authenticated user.

        Die Session/Authentifizierung kommt jetzt von django-allauth
        (bzw. allauth.headless). Hier wird nur das Userobjekt serialisiert.
        """
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
        """
        Update the role of a user with permission checks.
        """
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
