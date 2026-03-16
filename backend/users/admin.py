from django.contrib import admin

from .models import AuthPolicy, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "language", "is_new", "is_support_agent")
    list_filter = ("role", "language", "is_new", "is_support_agent")
    search_fields = ("user__email", "user__username", "user__first_name", "user__last_name")


@admin.register(AuthPolicy)
class AuthPolicyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "allow_admin_invite",
        "allow_self_signup_access_code",
        "allow_self_signup_open",
        "allow_self_signup_email_domain",
        "allow_self_signup_qr",
        "required_auth_factor_count",
        "signup_qr_expiry_days",
        "updated_at",
    )
