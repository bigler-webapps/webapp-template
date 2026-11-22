"""Isolated controller settings and routes never leak into normal profiles."""
import importlib
import os
import sys
from unittest.mock import patch

from django.apps import apps
from django.test import SimpleTestCase
from django.urls import Resolver404, resolve


class TestManagementIsolationTests(SimpleTestCase):
    def test_ordinary_settings_and_routes_exclude_controller(self):
        base_name = "django_core_micha.settings.settings_base"
        app_name = "backend.settings"
        original_base = sys.modules.get(base_name)
        original_app = sys.modules.get(app_name)
        try:
            for environment in ("local", "staging", "production"):
                with self.subTest(environment=environment), patch.dict(os.environ, {
                    "ENV_TYPE": environment, "DJANGO_SECRET_KEY": "test-only-settings-secret",
                }):
                    sys.modules.pop(base_name, None)
                    sys.modules.pop(app_name, None)
                    importlib.import_module(base_name)
                    module = importlib.import_module(app_name)
                    self.assertNotIn("django_core_micha.test_management", module.INSTALLED_APPS)
                    self.assertFalse(hasattr(module, "TEST_MANAGEMENT_ENABLED"))
                    with self.assertRaises(Resolver404):
                        resolve("/api/test-management/discovery/", urlconf=module.ROOT_URLCONF)
        finally:
            if original_base is not None:
                sys.modules[base_name] = original_base
            if original_app is not None:
                sys.modules[app_name] = original_app
        module = importlib.import_module("backend.test_settings")
        self.assertNotIn("django_core_micha.test_management", module.INSTALLED_APPS)
        self.assertFalse(hasattr(module, "TEST_MANAGEMENT_ENABLED"))
        with self.assertRaises(Resolver404):
            resolve("/api/test-management/discovery/", urlconf=module.ROOT_URLCONF)

    def test_disposable_settings_enable_controller_after_isolation_verification(self):
        if not apps.is_installed("django_core_micha.test_management"):
            self.skipTest("Requires dedicated test-management test settings")
        env = {"ENV_TYPE": "local", "DB_NAME": "isolated", "DB_USER": "isolated", "DB_PASSWORD": "test",
               "DB_HOST": "localhost", "DB_PORT": "5432", "FRONTEND_BUILD_DIR": "/tmp/build"}
        sys.modules.pop("backend.local_test_management_settings", None)
        try:
            with patch.dict(os.environ, env), patch("django_core_micha.test_management.isolation.verify_marker"):
                module = importlib.import_module("backend.local_test_management_settings")
                self.assertTrue(module.TEST_MANAGEMENT_ENABLED)
                self.assertIn("django_core_micha.test_management", module.INSTALLED_APPS)
                self.assertEqual(module.ROOT_URLCONF, "backend.test_management_urls")
                self.assertIn("test_management", resolve("/api/test-management/discovery/", urlconf=module.ROOT_URLCONF).func.view_class.__module__)
        finally:
            sys.modules.pop("backend.local_test_management_settings", None)
