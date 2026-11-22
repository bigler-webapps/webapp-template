"""Settings for isolated adapter unit tests without starting a stack."""
from .test_settings import *  # noqa: F401,F403

INSTALLED_APPS = [*INSTALLED_APPS, "django_core_micha.test_management"]  # noqa: F405
