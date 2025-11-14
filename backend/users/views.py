from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from .serializers import UserSerializer, InviteUserSerializer

import logging

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def csrf_token_view(request):
    """Return a simple JSON to ensure CSRF cookie is set on the client."""
    return JsonResponse({"detail": "CSRF cookie set"})


def send_password_reset_email(request, user: User, is_new_user: bool) -> None:
    """Generate a password reset token and send email with reset link."""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    frontend_base = request.build_absolute_uri("/")

    if is_new_user:
        subject = "Welcome to PROJECT_NAME"
        reset_url = f"{frontend_base.rstrip('/')}/invite/{uid}/{token}/"
        message = (
            "Hello!\n\n"
            "Welcome to PROJECT_NAME. Please set your password using the link below:\n"
            f"{reset_url}\n\n"
            "Best regards."
        )
    else:
        subject = "Password Reset Request"
        reset_url = f"{frontend_base.rstrip('/')}/reset/{uid}/{token}/"
        message = (
            "Hello!\n\n"
            "You requested a password reset. Please set your new password using the link below:\n"
            f"{reset_url}\n\n"
            "Best regards."
        )

    if getattr(settings, "ENV_TYPE", "") == "development":
        logger.info(f"[DEV] Password reset link for {user.email}: {reset_url}")
    else:
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD for users plus custom actions for login, invite, password reset and logout.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        open_actions = ["login", "reset_request", "non_auth_reset", "logout"]
        if self.action in open_actions:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated], url_path="current")
    def current(self, request):
        """Return or update the current authenticated user."""
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def login(self, request):
        """Authenticate user and start a session."""
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return Response(
            {
                "username": user.username,
                "is_new_user": getattr(user.profile, "is_new", False),
                "detail": "Login successful",
            }
        )

    @action(detail=False, methods=["post"])
    def invite(self, request):
        """Invite a user by email and send initial password link."""
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user, created = User.objects.get_or_create(email=email, defaults={"username": email})
        if created:
            user.profile.is_new = True
            user.profile.save()

        send_password_reset_email(request, user, is_new_user=True)
        return Response({"detail": f"Invitation sent to {email}", "created": created})

    @action(detail=False, methods=["post"], url_path="reset-request")
    def reset_request(self, request):
        """Start password reset flow for an existing user."""
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        send_password_reset_email(request, user, is_new_user=False)
        return Response({"detail": f"Password reset email sent to {email}"})

    @action(detail=False, methods=["post"])
    def logout(self, request):
        """Logout current user and clear session cookies."""
        logout(request)
        response = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie("sessionid")
        response.delete_cookie("csrftoken")
        return response

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
            return Response({"detail": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST)

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
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


class NonAuthenticatedPasswordResetView(APIView):
    """
    Validate password reset link and set new password without authentication.
    """

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Validate that a reset link is still valid."""
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            return Response({"detail": "Reset link is valid."}, status=status.HTTP_200_OK)
        return Response({"detail": "Reset link is invalid."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uidb64, token):
        """Set a new password using a valid reset link."""
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"detail": "New password not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Reset link is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.is_active = True
        user.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
