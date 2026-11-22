"""Test-management routing is confined to the disposable URL configuration."""
from django.apps import apps
from django.test import SimpleTestCase
from django.urls import Resolver404, resolve, reverse


class TestManagementUrlsTests(SimpleTestCase):
    def test_ordinary_urls_reject_unknown_api_routes(self):
        with self.assertRaises(Resolver404):
            resolve("/api/test-management/discovery/", urlconf="backend.urls")

    def test_dedicated_urls_mount_controller_and_privacy(self):
        if not apps.is_installed("django_core_micha.test_management"):
            self.skipTest("Requires dedicated test-management test settings")
        match = resolve("/api/test-management/discovery/", urlconf="backend.test_management_urls")
        self.assertIn("test_management", match.func.view_class.__module__)
        self.assertNotEqual(resolve("/api/privacy/manifest/", urlconf="backend.test_management_urls").url_name, "spa-entry")
        with self.assertRaises(Exception) as error:
            reverse("test-management-discovery", urlconf="backend.urls")
        from django.urls import NoReverseMatch
        self.assertIsInstance(error.exception, NoReverseMatch)
