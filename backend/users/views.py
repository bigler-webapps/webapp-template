from django.contrib.auth import get_user_model

from django_core_micha.auth.views import BaseUserViewSet

from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all().select_related("profile")
    serializer_class = UserSerializer
    current_patch_allowed_fields = BaseUserViewSet.current_patch_allowed_fields | {"is_new"}
