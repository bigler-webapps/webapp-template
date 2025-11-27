# users/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import render
from django_core.invitations.models import Invitation  # Annahme: Das Model liegt hier

class InvitationOnlySocialAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """
        Prüft, ob für die E-Mail des Social-Logins eine gültige Einladung vorliegt.
        Wenn nicht, wird die Registrierung blockiert.
        """
        email = sociallogin.user.email
        
        # 1. Prüfen: Gibt es diese E-Mail überhaupt in den Einladungen?
        # Passen Sie den Import und die Query an Ihr Invitation-Model an.
        if not Invitation.objects.filter(email=email, accepted=False).exists():
             return False # Blockiert den Signup Prozess
             
        return True