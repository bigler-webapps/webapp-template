# backend/auth_backends.py
#
# Email-based authentication backend. Looks up users by email instead of
# username. Inherits ModelBackend semantics (including is_active check).
#
# NOTE: Apps may override this for their own user-status semantics. Default
# enforces Django's standard is_active check — only active users can log in.

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 'username' parameter is interpreted as email.
        if not username or not password:
            return None
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        if not self.user_can_authenticate(user):
            return None

        if not user.check_password(password):
            return None

        return user
