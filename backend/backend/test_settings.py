from pathlib import Path

import environ

_env = environ.Env()
_env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_file.exists():
    environ.Env.read_env(str(_env_file))

from .settings import *  # noqa: F401,F403

# Outside Docker the DB container hostname "db" is not resolvable; use localhost.
# Inside Docker /.dockerenv exists and DB_HOST is already correct.
if not Path("/.dockerenv").exists():
    DATABASES["default"]["HOST"] = os.environ.get("TEST_DB_HOST", "localhost")


# Keep async/task infrastructure deterministic in tests.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# Speed up auth-heavy tests when they appear later.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Avoid writing test media into the project tree.
MEDIA_ROOT = BASE_DIR / "test_media"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
