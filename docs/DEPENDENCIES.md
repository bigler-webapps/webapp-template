# Dependencies

New apps should add optional Django Core Micha features only when their code uses them. Add the exact Core pin with the relevant extra: `ai` for AI integrations, `extraction` for document extraction, `push` for web push, or `scripts` when image or compose commands run Django Core scripts such as `generate-env`, `run-dev`, or `sync-secrets`.

Add Celery when the app needs background tasks. Add an exact Celery pin to `backend/requirements.txt`, create `backend/backend/celery.py` to configure and autodiscover tasks from Django settings, import the Celery app from `backend/backend/__init__.py`, add the required `CELERY_*` settings, and define a Celery worker service in the app's compose configuration.
