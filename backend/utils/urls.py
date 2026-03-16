from django.urls import path

from .views import CookieStatementView, PrivacyStatementView

urlpatterns = [
    path("privacy/", PrivacyStatementView.as_view(), name="privacy-statement"),
    path("cookie/", CookieStatementView.as_view(), name="cookie-statement"),
]
