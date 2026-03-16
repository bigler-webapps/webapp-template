from django.utils.translation import gettext as _
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CookieStatement, PrivacyStatement
from .serializers import CookieStatementSerializer, PrivacyStatementSerializer


class PrivacyStatementView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        statement = PrivacyStatement.objects.order_by("-uploaded_at").first()
        if not statement or not statement.file:
            return Response({"filename": None, "content": ""})

        try:
            content = PrivacyStatementSerializer(statement).data.get("content", "")
        except Exception:
            content = ""

        return Response({"filename": statement.file.name, "content": content})

    def post(self, request):
        uploaded = request.FILES.get("file")
        if not uploaded or not uploaded.name.lower().endswith(".md"):
            return Response(
                {"detail": _("Please upload a .md file.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        statement = PrivacyStatement.objects.create(file=uploaded)
        try:
            content = PrivacyStatementSerializer(statement).data.get("content", "")
        except Exception:
            content = ""

        return Response(
            {"filename": statement.file.name, "content": content},
            status=status.HTTP_201_CREATED,
        )


class CookieStatementView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        statement = CookieStatement.objects.order_by("-uploaded_at").first()
        if not statement or not statement.file:
            return Response({"filename": None, "content": ""})

        try:
            content = CookieStatementSerializer(statement).data.get("content", "")
        except Exception:
            content = ""

        return Response({"filename": statement.file.name, "content": content})

    def post(self, request):
        uploaded = request.FILES.get("file")
        if not uploaded or not uploaded.name.lower().endswith(".md"):
            return Response(
                {"detail": _("Please upload a .md file.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        statement = CookieStatement.objects.create(file=uploaded)
        try:
            content = CookieStatementSerializer(statement).data.get("content", "")
        except Exception:
            content = ""

        return Response(
            {"filename": statement.file.name, "content": content},
            status=status.HTTP_201_CREATED,
        )
