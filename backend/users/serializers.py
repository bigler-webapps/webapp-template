from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    is_new = serializers.BooleanField()
    accepted_privacy_statement = serializers.BooleanField()
    accepted_convenience_cookies = serializers.BooleanField()

    class Meta:
        model = UserProfile
        fields = (
            "role",
            "is_new",
            "accepted_privacy_statement",
            "accepted_convenience_cookies",
        )


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", required=False)
    accepted_privacy_statement = serializers.BooleanField(
        source="profile.accepted_privacy_statement",
        required=False,
    )
    accepted_convenience_cookies = serializers.BooleanField(
        source="profile.accepted_convenience_cookies",
        required=False,
    )
    is_new = serializers.BooleanField(source="profile.is_new", required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
            "role",
            "accepted_privacy_statement",
            "accepted_convenience_cookies",
            "is_new",
        )

    def update(self, instance, validated_data):
        """Update user instance and related profile in one call."""
        profile_data = validated_data.pop("profile", {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for attr, value in profile_data.items():
            setattr(instance.profile, attr, value)
        instance.profile.save()
        return instance


class InviteUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
