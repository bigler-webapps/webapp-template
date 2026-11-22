"""Dedicated disposable local settings for dcm test-management runs.

The controller token and instance id are supplied by the local bootstrap process.
This module never makes ordinary development, staging or production eligible.
"""
import os
from django.core.exceptions import ImproperlyConfigured
from django_core_micha.test_management.isolation import IsolationFailure, verify_marker

E2E_ORIGINAL_ENV_TYPE = os.environ.get("ENV_TYPE", "")
TEST_MANAGEMENT_ORIGINAL_ENV_TYPE = E2E_ORIGINAL_ENV_TYPE
if E2E_ORIGINAL_ENV_TYPE.lower() != "local":
    raise ImproperlyConfigured("Test management requires an original local environment.")
try:
    verify_marker()
except IsolationFailure as exc:
    raise ImproperlyConfigured("Test-management isolation has not been verified.") from exc
os.environ["ENV_TYPE"] = "local"

from .settings import *  # noqa: E402,F401,F403

DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ["DB_NAME"], "USER": os.environ["DB_USER"],
    "PASSWORD": os.environ["DB_PASSWORD"], "HOST": os.environ["DB_HOST"],
    "PORT": os.environ["DB_PORT"],
}}
ROOT_URLCONF = "backend.test_management_urls"
_build = Path(os.environ["FRONTEND_BUILD_DIR"])  # noqa: F405
TEMPLATES[0]["DIRS"] = [_build] + TEMPLATES[0]["DIRS"]  # noqa: F405
STATICFILES_DIRS = [_build / "static"]

# In DEBUG mode the application's ordinary URL configuration serves MEDIA_ROOT
# directly; the isolated profile must exercise the protected download routes.
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "[::1]"]
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = []
CORS_ALLOWED_ORIGIN_REGEXES = []
CORS_ALLOW_CREDENTIALS = False
CSRF_TRUSTED_ORIGINS = []
STORAGES = {**STORAGES, "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}}  # noqa: F405
# This instance exercises password login with synthetic addresses; it must not
# send mail or depend on live social-provider credentials.
EMAIL_PROVIDER = "console"
MAILERS = {**MAILERS, "default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}}  # noqa: F405
AUTH_METHODS = {**AUTH_METHODS, "social_login": False}  # noqa: F405

INSTALLED_APPS = [*INSTALLED_APPS, "django_core_micha.test_management"]

TEST_MANAGEMENT_ENABLED = True
TEST_MANAGEMENT_ISOLATED_INSTANCE = os.environ.get("TEST_MANAGEMENT_ISOLATED_INSTANCE") == "1"
TEST_MANAGEMENT_DISPOSABLE_STORAGE = os.environ.get("TEST_MANAGEMENT_DISPOSABLE_STORAGE") == "1"
TEST_MANAGEMENT_ISOLATED_DATABASE = os.environ.get("TEST_MANAGEMENT_ISOLATED_DATABASE") == "1"
TEST_MANAGEMENT_ISOLATED_MEDIA = os.environ.get("TEST_MANAGEMENT_ISOLATED_MEDIA") == "1"
TEST_MANAGEMENT_ISOLATED_CACHE = os.environ.get("TEST_MANAGEMENT_ISOLATED_CACHE") == "1"
TEST_MANAGEMENT_ISOLATED_SESSIONS = os.environ.get("TEST_MANAGEMENT_ISOLATED_SESSIONS") == "1"
TEST_MANAGEMENT_ISOLATED_BACKGROUND = os.environ.get("TEST_MANAGEMENT_ISOLATED_BACKGROUND") == "1"
TEST_MANAGEMENT_REMOTE_ACCESS = False
TEST_MANAGEMENT_INSTANCE_ID = os.environ.get("TEST_MANAGEMENT_INSTANCE_ID", "")
TEST_MANAGEMENT_CONTROLLER_TOKEN = os.environ.get("TEST_MANAGEMENT_CONTROLLER_TOKEN", "")
TEST_MANAGEMENT_BOOT_ID = os.environ.get("TEST_MANAGEMENT_BOOT_ID", "")
TEST_MANAGEMENT_CONTROLLER_TTL_SECONDS = 7200
# Replace the adapter path when adapting the account templates and fixture.
TEST_MANAGEMENT_ADAPTER = "users.test_management.TemplateTestManagementAdapter"
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "test_management_sessionid"
TEST_MANAGEMENT_CACHE_KEY_PREFIX = f"test-management-{TEST_MANAGEMENT_INSTANCE_ID}"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": TEST_MANAGEMENT_CACHE_KEY_PREFIX}}
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

