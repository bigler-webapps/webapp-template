from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

# Import aus deiner Lib
from django_core.auth.models import AbstractUserProfile 

User = get_user_model()

class UserProfile(AbstractUserProfile):
    """
    Erbt von AbstractUserProfile und fügt projektspezifische Rollen hinzu.
    """
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("supervisor", "Supervisor"),
        ("collaborator", "Collaborator"),
        ("none", "None"),
    ]

    # Nur das Feld 'role' ist hier noch nötig, der Rest kommt aus der Basisklasse
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="none")

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"

# Das Signal zum Erstellen des Profils muss LOKAL bleiben,
# da es das lokale 'UserProfile' Model benutzt.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Prüfung added für Robustheit
        if hasattr(instance, 'profile'):
            instance.profile.save()