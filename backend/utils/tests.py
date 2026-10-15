from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import CookieStatement, PrivacyStatement


class StatementViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="statement-admin@example.com",
            email="statement-admin@example.com",
            password="secret",
            is_superuser=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_missing_privacy_file_returns_unreadable_payload_and_logs(self):
        statement = PrivacyStatement.objects.create(
            file=ContentFile(b"# Privacy", name="privacy.md")
        )
        stored_name = statement.file.name
        statement.file.storage.delete(stored_name)

        with self.assertLogs("utils.views", level="ERROR") as logs:
            response = self.client.get(reverse("privacy-statement"))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["content"])
        self.assertEqual(response.data["error"], "unreadable")
        self.assertTrue(any("Error reading privacy statement" in line for line in logs.output))

    def test_invalid_cookie_file_returns_unreadable_payload_and_logs(self):
        CookieStatement.objects.create(file=ContentFile(b"\xff", name="cookie.md"))

        with self.assertLogs("utils.views", level="ERROR") as logs:
            response = self.client.get(reverse("cookie-statement"))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["content"])
        self.assertEqual(response.data["error"], "unreadable")
        self.assertTrue(any("Error reading cookie statement" in line for line in logs.output))

    def test_non_utf8_markdown_upload_is_rejected_for_both_statements(self):
        for url_name, model in (
            ("privacy-statement", PrivacyStatement),
            ("cookie-statement", CookieStatement),
        ):
            with self.subTest(url_name=url_name):
                response = self.client.post(
                    reverse(url_name),
                    {
                        "file": SimpleUploadedFile(
                            f"{url_name}.md",
                            b"\xff\xfe",
                            content_type="text/markdown",
                        )
                    },
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("UTF-8", response.data["detail"])
                self.assertEqual(model.objects.count(), 0)

    def test_valid_privacy_and_cookie_statements_round_trip(self):
        for url_name, content in (
            ("privacy-statement", "# Privacy\nText"),
            ("cookie-statement", "# Cookies\nText"),
        ):
            with self.subTest(url_name=url_name):
                response = self.client.post(
                    reverse(url_name),
                    {
                        "file": SimpleUploadedFile(
                            f"{url_name}.md",
                            content.encode("utf-8"),
                            content_type="text/markdown",
                        )
                    },
                )
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.data["content"], content)

                get_response = self.client.get(reverse(url_name))
                self.assertEqual(get_response.status_code, 200)
                self.assertEqual(get_response.data["content"], content)
