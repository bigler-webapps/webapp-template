from rest_framework import serializers

from .models import CookieStatement, PrivacyStatement


class PrivacyStatementSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = PrivacyStatement
        fields = ["file", "uploaded_at", "content"]

    def get_content(self, obj):
        obj.file.open("rb")
        try:
            return obj.file.read().decode("utf-8")
        finally:
            obj.file.close()


class CookieStatementSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = CookieStatement
        fields = ["file", "uploaded_at", "content"]

    def get_content(self, obj):
        obj.file.open("rb")
        try:
            return obj.file.read().decode("utf-8")
        finally:
            obj.file.close()
