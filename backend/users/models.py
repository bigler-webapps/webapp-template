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


# --- IN users/models.py EINFÜGEN ---
import traceback
import sys
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(pre_save, sender=get_user_model())
def debug_password_wiping(sender, instance, **kwargs):
    # Nur prüfen, wenn der User schon existiert (kein Create)
    if instance.pk:
        try:
            # Den aktuellen Zustand aus der DB laden
            old_user = sender.objects.get(pk=instance.pk)
            
            # Hatte er ein Passwort? Und hat er jetzt keins mehr (oder ein ungültiges)?
            if old_user.has_usable_password() and not instance.has_usable_password():
                msg = (
                    f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                    f"ALARM: Das Passwort für {instance.email} wird gerade gelöscht!\n"
                    f"Vorher: {old_user.password[:10]}...\n"
                    f"Nachher: {instance.password}\n"
                    f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                )
                # Wir schreiben direkt in sys.stdout und flushen, damit Docker es sofort zeigt
                sys.stdout.write(msg)
                traceback.print_stack(file=sys.stdout)
                sys.stdout.flush()
        except sender.DoesNotExist:
            pass
# -----------------------------------