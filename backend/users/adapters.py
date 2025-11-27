# users/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class InvitationOnlySocialAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """
        Erlaubt den Social Login NUR, wenn die E-Mail-Adresse bereits 
        als User in der Datenbank existiert (d.h. der User wurde eingeladen/vorerstellt).
        """
        User = get_user_model()
        email = sociallogin.user.email
        
        # Suchen wir nach einem existierenden Nutzer mit dieser E-Mail
        # (Case-insensitive Suche ist sicherer: 'email__iexact')
        if User.objects.filter(email__iexact=email).exists():
            return True
        
        # Optional: Loggen Sie den Fehlversuch, damit Sie sehen, wer abgelehnt wurde
        # print(f"Login abgelehnt für nicht eingeladene Email: {email}")
        return False