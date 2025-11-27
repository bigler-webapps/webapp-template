from pathlib import Path
import environ
import os
from corsheaders.defaults import default_headers

# 1. Initialize Environment
env = environ.Env(
    DEBUG=(bool, False),
    EMAIL_PORT=(int, 587),
    EMAIL_USE_TLS=(bool, True),
)

# 2. Base Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-key")
DEBUG = env("DEBUG")

# 3. Hosts & Networking (Read directly from generated .env)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_URLS", default=[])
CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS
PUBLIC_ORIGIN = env("PUBLIC_ORIGIN", default="http://localhost:3000")

# Security Headers (Apply only if not in debug, or rely on Traefik)
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_REFERRER_POLICY = "same-origin"

# Cookies
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
# Only secure cookies if not debugging or explicitly requested
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# 4. Application Definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    
    # Third Party
    "corsheaders",
    "rest_framework",
    "channels",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "allauth.headless",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",

    # Local
    "users",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_MODULE = env("DJANGO_ROOT_MODULE", default="project_template_app")

ROOT_URLCONF = f"{ROOT_MODULE}.urls"
WSGI_APPLICATION = f"{ROOT_MODULE}.wsgi.application"
ASGI_APPLICATION = f"{ROOT_MODULE}.asgi.application"
SITE_ID = 1

# 5. Database
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        
        # --- SAFE BUILD-TIME DEFAULTS ADDED HERE ---
        # These dummy values are used ONLY during the Docker build (collectstatic)
        # They are overridden by the real .env values at runtime.
        "NAME": env("DB_NAME", default="db_build_dummy"), 
        "USER": env("DB_USER", default="user_build_dummy"),
        "PASSWORD": env("DB_PASSWORD", default="pass_build_dummy"),
        # HOST/PORT usually have defaults or are set via env.Env() init, 
        # but adding them here ensures safety.
        "HOST": env("DB_HOST", default="db"), 
        "PORT": env("DB_PORT", default="5432"),
    }
}

# 6. Channels / Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(env("REDIS_HOST", default="redis"), 6379)],
        },
    },
}

# 7. Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 8. Templates / Static / Media
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

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
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

# 9. Auth & Allauth
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ]
}

ACCOUNT_ADAPTER = "allauth.account.adapter.DefaultAccountAdapter"

# 1. Database Model Config (Keep this)
# This ensures the DB doesn't expect a username
ACCOUNT_USER_MODEL_USERNAME_FIELD = None 
ACCOUNT_UNIQUE_EMAIL = True

# 2. Login Method (Keep this)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_EMAIL_VERIFICATION = "optional"

# 3. Form Configuration (THE FIX)
# - We remove 'username' from this list to satisfy "No Username".
# - We add 'email*' with an asterisk to satisfy "Email Required".
# - We include password fields explicitly as per the new warning recommendation.
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "password1*",
    # "password2*", # Uncomment if you want "Confirm Password" field
]

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
LOGIN_REDIRECT_URL = "/"
SOCIALACCOUNT_LOGIN_ON_GET = False 

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": env("GOOGLE_CLIENT_ID", default=""),
            "secret": env("GOOGLE_SECRET", default=""),
            "key": ""
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        }
    },
    "microsoft": {
        "APP": {
            "client_id": env("MICROSOFT_CLIENT_ID", default=""),
            "secret": env("MICROSOFT_SECRET", default=""),
            "key": "",
            # Bei Microsoft oft nötig, um Multi-Tenant vs Single-Tenant zu steuern:
            # "settings": {
            #    "tenant": env("MICROSOFT_TENANT_ID", default="common"),
            # }
        },
        "SCOPE": ["User.Read"], 
        # "tenant": "organizations", # oder 'common' oder die Tenant ID
    }
}

HEADLESS_ONLY = True
HEADLESS_CLIENTS = ["browser"]
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": f"{PUBLIC_ORIGIN}/email-verify/{{key}}",
    "account_reset_password": f"{PUBLIC_ORIGIN}/reset-request-password",
    "account_reset_password_from_key": f"{PUBLIC_ORIGIN}/password-reset/{{key}}",
    "account_signup": f"{PUBLIC_ORIGIN}/signup",
    "socialaccount_login_error": f"{PUBLIC_ORIGIN}/login?social=error",
}

MFA_ADAPTER = "allauth.mfa.adapter.DefaultMFAAdapter"
MFA_WEBAUTHN_RP_NAME = "Project Template"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + ["X-Admin-Token", "X-CSRFToken"]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Zurich"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 10. Logging (Compacted)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        # Use the dynamic variable here as the key!
        ROOT_MODULE: {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO"
        },
    },
}