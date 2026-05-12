# backend/celery.py
#
# Celery bootstrap. Loads config from Django settings (CELERY_*) and
# auto-discovers tasks from installed apps (each app's tasks.py).

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

# Load configuration from Django settings (all CELERY_* variables).
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from registered Django apps.
app.autodiscover_tasks()
