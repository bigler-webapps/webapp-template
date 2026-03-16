from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_core_micha.auth.models import AbstractAuthPolicy, AbstractUserProfile

User = get_user_model()


class UserProfile(AbstractUserProfile):
    def __str__(self) -> str:
        return f"{self.user.email} ({self.role})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    profile, _ = UserProfile.objects.get_or_create(user=instance)
    if not created:
        profile.save()


class AuthPolicy(AbstractAuthPolicy):
    pass
