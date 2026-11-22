from django.conf import settings
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse
from rest_framework.test import APIClient

from django_core_micha.privacy.guard import has_grant
from django_core_micha.privacy.manifest import validate_manifest_setting


class PrivacyAdoptionTests(TestCase):
    def test_manifest_contains_only_necessary_services_and_live_cookie_names(self):
        manifest, errors = validate_manifest_setting(settings.DCM_PRIVACY)
        self.assertEqual(errors, [])
        self.assertEqual((manifest["app"], manifest["site"]), ("webapp-template", "webapp-template"))
        self.assertEqual(manifest["locales"], ["de", "en", "fr"])
        self.assertEqual([purpose["id"] for purpose in manifest["purposes"]], ["necessary"])
        purpose = manifest["purposes"][0]
        self.assertTrue(purpose["required"])
        cookies = {item["name"] for service in purpose["services"] for item in service["browser_storage"] if item["kind"] == "cookie"}
        self.assertTrue({settings.SESSION_COOKIE_NAME, settings.CSRF_COOKIE_NAME} <= cookies)
        self.assertTrue(all(set(refs) == set(manifest["locales"]) for refs in manifest["notice"]["documents"].values()))

    def test_anonymous_reads_and_unknown_grants_fail_closed(self):
        self.assertIsNotNone(resolve("/api/csrf/"))
        client = APIClient()
        for name in ("dcm-privacy-manifest", "dcm-privacy-choices"):
            response = client.get(reverse(name), secure=True)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(any(key.startswith("dcm_privacy_") for key in response.cookies))
        self.assertFalse(has_grant(RequestFactory().get("/"), "unknown-purpose"))
