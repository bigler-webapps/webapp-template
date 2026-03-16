from pathlib import Path

from django_core_micha.settings.settings_base import *  # noqa: F403,F401

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_NAME = env("PROJECT_NAME", default="Project Template App")  # noqa: F405

LOCAL_APPS = [
    "allauth.headless",
    "users",
    "utils",
]

INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS  # noqa: F405

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_MODULE = env("DJANGO_ROOT_MODULE", default="backend")  # noqa: F405
ROOT_URLCONF = f"{ROOT_MODULE}.urls"
WSGI_APPLICATION = f"{ROOT_MODULE}.wsgi.application"
ASGI_APPLICATION = f"{ROOT_MODULE}.asgi.application"

SITE_ID = env.int("DJANGO_SITE_ID", default=1)  # noqa: F405

ROLE_DEFINITIONS = {
    "none": {"level": 0, "label": "None"},
    "collaborator": {"level": 1, "label": "Collaborator"},
    "supervisor": {"level": 2, "label": "Supervisor"},
    "admin": {"level": 3, "label": "Admin"},
}

DEFAULT_ROLE_CODE = "none"
INVITE_MIN_ROLE_LEVEL = 2
INVITE_ADMIN_ROLES = ("supervisor",)
AUTH_POLICY_WRITE_MIN_ROLE_LEVEL = 3
SUPPORT_ASSIGN_ROLE_LEVEL = 3

TEMPLATES = [  # noqa: F405
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
LOCALE_PATHS = [BASE_DIR / "locale"]

LANGUAGE_CODE = "de"
LANGUAGES = [
    ("de", "Deutsch"),
    ("en", "English"),
    ("fr", "Français"),
]

HEADLESS_ONLY = env.bool("HEADLESS_ONLY", default=True)  # noqa: F405
HEADLESS_CLIENTS = ["browser"]  # noqa: F405

ACCESS_CODE_REGISTRATION_ENABLED = True
ACCESS_CODE_ADMIN_ROLES = ("supervisor",)
AUTH_POLICY_MODEL = "users.AuthPolicy"

AUTH_METHODS = {
    "password_login": True,
    "password_reset": True,
    "signup": True,
    "password_change": True,
    "social_login": True,
    "social_providers": ["google", "microsoft"],
    "passkey_login": True,
    "passkeys_manage": True,
    "mfa_totp": True,
    "mfa_recovery_codes": True,
}

LOGGING["loggers"]["project_template"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "DEBUG" if DEBUG else "INFO",  # noqa: F405
}
