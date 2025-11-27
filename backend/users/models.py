from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("supervisor", "Supervisor"),
        ("collaborator", "Collaborator"),
        ("none", "None"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="none")
    is_new = models.BooleanField(default=True)
    accepted_privacy_statement = models.BooleanField(default=False)
    accepted_convenience_cookies = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update the user profile whenever the User object is saved."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()

