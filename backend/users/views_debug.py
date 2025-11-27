# z.B. in users/views_debug.py
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class WhoAmI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = getattr(request, "user", None)
        return Response({
            "is_authenticated": bool(getattr(user, "is_authenticated", False)),
            "username": getattr(user, "email", None) or getattr(user, "username", None),
        })
