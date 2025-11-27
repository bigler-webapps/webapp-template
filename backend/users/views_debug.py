from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Falls du nicht global über REST_FRAMEWORK konfigurierst:
from allauth.headless.contrib.rest_framework.authentication import (
    XSessionTokenAuthentication,
)

class WhoAmI(APIView):
    # Wenn du REST_FRAMEWORK schon angepasst hast, kannst du die Zeile auch weglassen
    authentication_classes = [XSessionTokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response(
            {
                "is_authenticated": user.is_authenticated,
                "id": user.id if user.is_authenticated else None,
                "email": getattr(user, "email", ""),
            }
        )
