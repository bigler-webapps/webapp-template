from pathlib import Path
import os
import logging
from corsheaders.defaults import default_headers

# --- Helper ---
def get_list(var_name):
    """Parses a comma-separated string from environment into a list."""
    val = os.environ.get(var_name, "")
    return [x.strip() for x in val.split(",") if x.strip()]

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# 1) ENV-Umschaltung & Basis
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_TYPE = os.environ.get("ENV_TYPE", "production")
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-key")

# Public Origin für Frontend-URLs (wichtig für Allauth Headless)
PUBLIC_ORIGIN = os.environ.get("PUBLIC_ORIGIN", "http://localhost:3000")
FRONTEND_BASE_URL = PUBLIC_ORIGIN

if ENV_TYPE == "development":
    DEBUG = True
    SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    SESSION_COOKIE_AGE = 1209600
    logger.info("Running in DEVELOPMENT mode.")

    ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]

    # Lokale URLs für CORS/CSRF
    LOCAL_ORIGINS = [
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:8125", "http://127.0.0.1:8125",
        # Falls HTTPS lokal genutzt wird:
        "https://localhost:3000",
    ]

    CSRF_TRUSTED_ORIGINS = LOCAL_ORIGINS
    CORS_ALLOWED_ORIGINS = LOCAL_ORIGINS
    
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

else:
    DEBUG = False
    SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    SESSION_COOKIE_AGE = 1209600
    logger.info("Running in PRODUCTION mode.")

    # WICHTIG: Aus Env (definiert durch GitHub Action / .env)
    ALLOWED_HOSTS = get_list("DJANGO_ALLOWED_HOSTS")

    # Security Headers
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_REFERRER_POLICY = "same-origin"

    # WICHTIG: Aus Env (definiert durch GitHub Action / .env)
    PROD_ORIGINS = get_list("CSRF_TRUSTED_URLS")

    CSRF_TRUSTED_ORIGINS = PROD_ORIGINS
    CORS_ALLOWED_ORIGINS = PROD_ORIGINS
    
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Cookies
IS_CROSS_SITE = os.environ.get("CROSS_SITE", "0") == "1"
SESSION_COOKIE_SAMESITE = "None" if IS_CROSS_SITE else "Lax"
CSRF_COOKIE_SAMESITE    = "None" if IS_CROSS_SITE else "Lax"
SESSION_COOKIE_SECURE = True if (ENV_TYPE != "development" or IS_CROSS_SITE) else False
CSRF_COOKIE_SECURE    = True if (ENV_TYPE != "development" or IS_CROSS_SITE) else False

# -------------------------------------------------------------------
# 2) Gemeinsame Basis-Config (Static/Media)
# -------------------------------------------------------------------
X_FRAME_OPTIONS = "DENY"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise Storage für effizientes Caching/Hashing
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    "X-Admin-Token",
    "X-CSRFToken",
]

# -------------------------------------------------------------------
# 3) Datenbank-Setup
# -------------------------------------------------------------------
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}

# -------------------------------------------------------------------
# 4) Email
# -------------------------------------------------------------------
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# -------------------------------------------------------------------
# 5) Channels / Redis
# -------------------------------------------------------------------
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, 6379)],
        },
    },
}

# -------------------------------------------------------------------
# 6) Auth & Allauth Configuration
# -------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ]
}

# Allauth Settings
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_ADAPTER = "allauth.account.adapter.DefaultAccountAdapter"

ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "password1*",
]

# Headless Config (API only)
HEADLESS_ONLY = True
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": f"{FRONTEND_BASE_URL}/email-verify/{{key}}",
    "account_reset_password": f"{FRONTEND_BASE_URL}/reset-request-password",
    "account_reset_password_from_key": f"{FRONTEND_BASE_URL}/password-reset/{{key}}",
    "account_signup": f"{FRONTEND_BASE_URL}/signup",
    "socialaccount_login_error": f"{FRONTEND_BASE_URL}/login?social=error",
}
HEADLESS_CLIENTS = ["browser"]

MFA_ADAPTER = "allauth.mfa.adapter.DefaultMFAAdapter"
MFA_WEBAUTHN_RP_NAME = "Project Template"

# -------------------------------------------------------------------
# 7) Apps / Middleware / URLs
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.gis",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    "corsheaders",
    "rest_framework",
    "channels",

    "users",  # Eigene User App

    # Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "allauth.headless",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",
]

SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project_template_app.urls"

TEMPLATES = [
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

WSGI_APPLICATION = "project_template_app.wsgi.application"
ASGI_APPLICATION = "project_template_app.asgi.application"

# -------------------------------------------------------------------
# 8) Passwords / i18n / Defaults
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Zurich"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "project_template_app": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}