# users/signals.py
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
import logging
from django.contrib.auth import get_user_model
from allauth.socialaccount.signals import pre_social_login

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

@receiver(pre_social_login)
def force_auto_connect_on_email_match(sender, request, sociallogin, **kwargs):
    """
    Forces the connection of a social account to a local account 
    if the email addresses match perfectly. 
    Bypasses the 'signup form' interruption even if the email verification status is unclear.
    """
    # 1. If the social account is already linked, do nothing.
    if sociallogin.is_existing:
        return

    # 2. Check if we have an email from the provider
    if not sociallogin.email_addresses:
        return
    
    social_email = sociallogin.email_addresses[0].email
    User = get_user_model()

    try:
        # 3. Find the local user with this email (case-insensitive for safety)
        user = User.objects.get(email__iexact=social_email)
        
        # 4. CRITICAL: Manually trigger the connection
        # This tells allauth: "This social login BELONGS to this user."
        sociallogin.connect(request, user)
        
        logger.info(f"Auto-connected Microsoft account for {social_email} to existing user.")

    except User.DoesNotExist:
        # If user does not exist, do nothing. 
        # Your 'InvitationOnlySocialAdapter' will block the signup later.
        pass