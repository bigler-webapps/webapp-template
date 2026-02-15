# backend/settings.py

from pathlib import Path
from django_core_micha.settings.settings_base import *

BASE_DIR = Path(__file__).resolve().parent.parent

# Templates / Static / Media (pfadabhängig)
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Root-Konfiguration – bei dir immer 'backend'
ROOT_URLCONF = "backend.urls"
WSGI_APPLICATION = "backend.wsgi.application"
ASGI_APPLICATION = "backend.asgi.application"

# Sites
SITE_ID = 1

# Lokale Apps
LOCAL_APPS = [
    "users",
]

INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS


ACCESS_CODE_REGISTRATION_ENABLED = True  # oder False

# Welche Rollen dürfen Codes verwalten (neben superuser/staff)?
ACCESS_CODE_ADMIN_ROLES = ("admin", "supervisor")
INVITE_ADMIN_ROLES = ("admin", "supervisor")


# Platz für projektspezifische Overrides bei Bedarf
# z.B. andere TIME_ZONE, zusätzliche LOGGING-Einträge, etc.
