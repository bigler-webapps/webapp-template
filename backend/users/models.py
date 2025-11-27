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


# --- IN users/models.py (KORRIGIERT) ---
import sys
import traceback
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

# WICHTIG: sender als String übergeben, nicht als Klasse aufrufen!
@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def debug_password_wiping(sender, instance, **kwargs):
    # Nur prüfen, wenn der User schon existiert (kein Create)
    if instance.pk:
        try:
            # Hier drin ist es sicher, auf die DB zuzugreifen
            # sender ist zur Laufzeit die User-Klasse
            old_user = sender.objects.get(pk=instance.pk)
            
            # Hatte er ein Passwort? Und hat er jetzt keins mehr?
            # Wir prüfen auf "unusable" (das ! am Anfang des Hashs) oder leeren String
            old_has_pw = old_user.password and not old_user.password.startswith('!')
            new_has_no_pw = not instance.password or instance.password.startswith('!')

            if old_has_pw and new_has_no_pw:
                msg = (
                    f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                    f"ALARM: Das Passwort für {instance.email} wird gerade gelöscht!\n"
                    f"Vorher Hash Start: {old_user.password[:10]}...\n"
                    f"Nachher Hash: {instance.password}\n"
                    f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                )
                sys.stdout.write(msg)
                # Stack Trace ausgeben, um den Übeltäter zu finden
                traceback.print_stack(file=sys.stdout)
                sys.stdout.flush()
        except sender.DoesNotExist:
            pass
# ---------------------------------------