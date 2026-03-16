from django.contrib.auth import get_user_model
from rest_framework import serializers

from django_core_micha.auth.serializers import BaseUserSerializer

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User


class InviteUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
