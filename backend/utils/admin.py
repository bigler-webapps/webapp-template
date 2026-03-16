from django.contrib import admin

from .models import CookieStatement, PrivacyStatement


@admin.register(PrivacyStatement)
class PrivacyStatementAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_at")
    ordering = ("-uploaded_at",)


@admin.register(CookieStatement)
class CookieStatementAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_at")
    ordering = ("-uploaded_at",)
