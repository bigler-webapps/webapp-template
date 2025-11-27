# users/signals.py
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def prevent_password_wipe(sender, instance, **kwargs):
    """
    Prevents django-allauth from wiping the local password when 
    linking a social account (SSO) to an existing account.
    """
    # Only check on updates, not creation
    if instance.pk:
        try:
            # Fetch current state from DB
            old_user = sender.objects.get(pk=instance.pk)
            
            # Condition 1: User had a valid password before
            has_old_pw = old_user.password and not old_user.password.startswith('!')
            
            # Condition 2: Something (allauth) is trying to set an unusable password
            is_wiping_pw = not instance.password or instance.password.startswith('!')

            if has_old_pw and is_wiping_pw:
                # Restore the old password hash
                instance.password = old_user.password
                logger.info(f"Prevented password wipe for user {instance.email}")
                
        except sender.DoesNotExist:
            pass