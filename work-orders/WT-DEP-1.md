# WT-DEP-1 — Lean template: only what every new app needs

Part of the estate dependency reduction decided 2026-10-15 (operator + Expertenchat): one
order per app, after `django-core-micha` `DCM-DEPS-3` and `ui-core-micha` `UCM-DEP-2` have
released. Source of the item lists: a per-repo usage audit on 2026-10-15 (grep-based, so
every item is re-checked against R1 before it goes).

# A. Envelope

## Goal & expected outcome

- Ziel: an app scaffolded from webapp-template starts with only what every app needs; anything
  else is added by the app when it uses it.
- Expected outcome: no manifest line without a use; the template runs on the dcm major from
  `DCM-DEPS-3` and on ucm 4.0.0 with exactly the extras and peers it needs, on psycopg 3,
  with test tooling out of the production image and without `react-helmet`; a freshly
  scaffolded app builds its image, boots, and passes its own test suite. (The template has no
  staging or production deployment of its own — its deploy job skips on the template repo.)
- Current pins: django-core-micha 2.44.2, ui-core-micha 3.12.0.

## Estate rules (decided 2026-10-15 — they govern every item in "Scope")

- **R1 Removal test.** A package leaves the manifest when nothing uses it: not the app's code, its
  settings (`INSTALLED_APPS`, `MIDDLEWARE`, string settings), Dockerfile, compose files, CI, test
  config keys, vite/eslint config, nor any package that stays as a required peer. Package names that
  differ from import names count (`Pillow` -> `PIL`, `PyYAML` -> `yaml`, ...).
- **R2 Transitive pins stay (INF-61).** A backend package the app does not use itself, but that the
  resolved install still contains because something else requires it, keeps its exact pin. Its line
  goes only when, after this order's dcm bump and extras choice, nothing in the resolved install
  requires it any more. Decide from the resolved install, not by reading manifests.
- **R3 dcm extras.** The dcm major released by `DCM-DEPS-3` moves optional features into extras
  (`ai`: openai, anthropic · `extraction`: pypdf, Pillow · `push`: pywebpush · `scripts`: PyYAML —
  authoritative list: that release's CHANGELOG migration table). The app requests exactly the
  extras whose dcm features it uses; a dcm CLI script run inside the image (`generate-env`,
  `run-dev`, `sync-secrets`, ...) counts as using `scripts`.
- **R4 One Postgres driver.** The app runs on psycopg 3 only: `psycopg2-binary` leaves,
  `psycopg[binary]` is pinned exactly. The `pool` extra stays only where `DATABASES` `OPTIONS`
  configures a pool.
- **R5 ucm peers.** After the bump to ucm 4.0.0 (`UCM-DEP-2`), the app declares exactly the peers
  4.0.0 marks required, plus the optional peers of the sub-paths it imports (`./charts`, `./qr`,
  `./markdown`); app imports of moved components are rewritten to the sub-path. A peer the app
  declared only because an older ucm required it (e.g. `react-helmet`, `qrcode.react`,
  `@mui/x-charts`) goes when the app's own code does not import it.
- **R6 Test tooling out of the production image.** pytest and its plugins move to
  `backend/requirements-test.txt` (first line `-r requirements.txt`, exact pins), installed only by
  the Dockerfile's test stage — provided the app's CI receives its Python test dependencies through
  that Dockerfile stage. If CI installs `requirements.txt` directly instead, the split is not made
  in this order. Test-only frontend packages sit in `devDependencies`.
- **R7 Undeclared imports get declared.** A package the app imports directly but does not declare
  is declared (backend: exact pin; frontend: `package.json`).
- **R8 Lockfiles and pnpm.** Every manifest change is reflected in the regenerated lockfile(s); the
  pnpm version the Dockerfile activates equals `packageManager` in `frontend/package.json`.
- **R9 Scaffolding goes with its package.** Files, settings and config keys that exist only to wire
  a removed package (e.g. `celery.py`, `dev_celery_autoreload.py`, `CELERY_*` settings,
  `asyncio_mode` in `pytest.ini`, a `vite.config` alias) are removed with it.
- **R10 Verify items.** Where an item says "verify", the stated check decides. If the check is
  inconclusive, the package stays and the register note names it — never remove on assumption.

## Scope — this app

### Shared-core bump

- dcm to the major released by `DCM-DEPS-3`; ucm to 4.0.0 (R5).
- Default extras for a new app (operator decision 2026-10-15): only `scripts`, and only if the
  template's image or compose files run a dcm CLI script (`generate-env`, `run-dev`,
  `sync-secrets`, ...); otherwise none. `ai`, `extraction` and `push` are added by an app when it
  uses the feature — the Celery docs section below gets a sibling sentence saying so.

### Backend

- Celery scaffolding (R9): `backend/backend/celery.py`, `backend/dev_celery_autoreload.py`, any `CELERY_*` settings and the `celery` pin — verify first: no `@shared_task`/`.delay`/`apply_async` in the app or the pinned dcm, and no worker or beat service in compose/Dockerfile; new apps add Celery when they need it (see Docker / repo)
- `django-crontab` (not in `INSTALLED_APPS`, no `CRONJOBS`)
- `python-dotenv`: per R2 (uvicorn[standard] may bring it)
- `daphne` (rollback-only pin; CMD is gunicorn + UvicornWorker)
- `psycopg2-binary` -> `psycopg[binary]` (R4) — drop the unused `[pool]` extra
- `requests`, `PyJWT[crypto]`: per R2
- `packaging` is imported by `backend/tests/test_requirements_pinned.py` but undeclared: exact pin in the test requirements (R7)
- Test tooling split per R6 (`pytest`, `pytest-django` and further pytest plugins)

### Frontend

- `@eslint/js` (devDependency; `eslint.config.js` does not import it)
- `@mui/system` (direct entry; no import, `@mui/material` brings it)
- `@testing-library/user-event` (no test uses it)
- `react-helmet` (operator decision 2026-10-15, template only): `src/pages/Home.jsx` and
  `src/pages/WelcomePage.jsx` render a native React 19 `<title>` instead of `<Helmet>`, with the
  same title text; the package leaves `package.json`

### Docker / repo

- A short section in the template's developer docs: how a new app adds Celery (pin, `celery.py`, the `__init__` import, worker service in compose)

### Verify items (R10)

- `pytest-cov`: stays only if the shared CI invokes coverage for template-derived apps; otherwise it goes with `.coveragerc`

## Non-goals / do-not-touch

- No version upgrade of a package that stays, apart from the dcm/ucm bump and what R4, R7 and R8
  require.
- No behaviour change: this order removes and re-declares; it does not refactor working code
  beyond the named one-site replacements.
- The shared CI (`workflow-templates` `app-ci.yml`) is not changed.
- Existing apps are not touched — each has its own order (they keep app-side `react-helmet` until
  their own follow-up).

## Tier · precondition / gate

- Tier 3: a shared-core bump that removes dependencies the template uses today, the Postgres
  driver switch, Dockerfile changes — and every app scaffolded afterwards inherits the result.
- Precondition: blocked until `DCM-DEPS-3` and `UCM-DEP-2` are released.

## Risks

- Every future app inherits a mistake here; a missing package shows only when the new app first
  builds or boots.
- psycopg2 -> psycopg 3 changes the driver that scaffolded apps will run in production;
  differences show in edge cases (custom type adaptation, server-side cursors, timezone handling).
- A removed package was reached through a path the audit missed (string import, plugin entry
  point, management command): import error at boot or on one code path.
- The ucm 4.0.0 sub-path move: a missed import breaks the frontend build.
- Native `<title>`: the browser-tab title on the two pages must stay the same text.

## Required tests to WRITE

- Driver: under the test settings `django.db.connection` uses psycopg 3 (the backend's `Database`
  module is `psycopg`).
- Titles: `Home` and `WelcomePage` each set the document title to today's text (one case per page).
- No other new tests — pure removals need none.
