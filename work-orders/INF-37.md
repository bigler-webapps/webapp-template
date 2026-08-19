# INF-37 — Django 6.1 + dcm 2.43.0 (webapp-template)

Cross-repo WO. Canonical Envelope + full rationale: `webapp-management/work-orders/INF-37.md`.
This file is webapp-template's implementation slice — same ID, same Envelope, this repo's map.

## This repo's scope

Two-line pin bump in `backend/requirements.txt`: `django-core-micha` → `2.43.0`, `Django` → `6.1`.

## Landed

Commit `a106e55`. This app has no deployment/database and is one of OPS-4's two `pre-existing-red`
apps (20 failed/2 passed at both pins — an unrelated, already-known `test_settings.py` placeholder
bug, not caused by this bump). Per the WO's own instruction: record and proceed, don't let a red
baseline block the bump, don't claim a green one. Matters out of proportion since every new app
scaffolds from this repo's current state.
