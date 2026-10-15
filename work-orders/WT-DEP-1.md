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


# B. Implementation map — ADDRESSED TO THE IMPLEMENTER

## Target and ownership

Target working directory: `C:/Users/Micha Bigler/Documents/webapps/webapp-template`.
You own only `backend/Dockerfile`, `backend/backend/test_settings.py`,
`backend/backend/celery.py`, `backend/dev_celery_autoreload.py`, `backend/pytest.ini`,
`backend/.coveragerc`, `backend/tests/test_database_driver.py`,
`frontend/src/pages/Home.jsx`, `frontend/src/pages/WelcomePage.jsx`,
`frontend/src/pages/PageTitles.test.jsx`, `frontend/vite.config.mts`, and
`docs/DEPENDENCIES.md`. Preserve other agents' changes. No joined E2E harness is present.

## Verified context and invariants

- Operator's handover explicitly supersedes the Envelope's ucm 4.0.0 target with published
  **4.0.1**. dcm target is published **3.0.0**. The Orchestrator owns manifests, installs and lockfiles.
- `backend/Dockerfile:31` backend_base installs runtime requirements; `:67` backend_test is
  currently empty; install requirements-test.txt there only. Final derives from backend_base.
  Both frontend build stages must activate packageManager pnpm 11.5.1 (currently Docker 11.1.3).
  Retire the rollback-only daphne comment but keep all runtime/proxy settings unchanged.
- `backend/backend/__init__.py` is empty. No Celery task/decorator/call in app or dcm 3.0.0
  source; no compose worker/beat. Delete the two named Celery scripts and test_settings.py
  CELERY_* block; retain CHANNEL_LAYERS and all remaining test settings unchanged.
- `backend/pytest.ini` explicitly names test files. Add test_database_driver.py to testpaths.
  Remove pytest-asyncio/asyncio_mode: backend/test_ws_inventory.py is synchronous, and no app async test uses the plugin.
- CI `ci.yml` passes `backend-target: backend_test`; shared app-ci.yml runs pytest without
  coverage flags, so pytest-cov and backend/.coveragerc leave under R10.
- uv resolution on Python 3.14/Linux of the dcm 3.0.0 candidate proves requests/PyJWT remain
  through allauth/anymail, python-dotenv/PyYAML through uvicorn[standard]. Preserve their exact
  existing pins. No app image/compose command executes dcm scripts, so dcm uses NO extras.
  Pillow has no app use and leaves. Do not expand this audit or modify shared-core repos.
- `frontend/src/pages/Home.jsx:6,15` Helmet wraps only t("Home.PAGE_TITLE"); replace wrapper
  with native title preserving that key. WelcomePage.jsx:11,36 similarly uses
  t("Welcome.PAGE_TITLE"). Preserve routing, auth and submission behavior.
- `frontend/src/pages/PageTitles.test.jsx` tests both real pages, AuthContext provider, router
  and i18n; assert translated document.title after render. Existing tests in App.test.jsx and
  AuthRoutesIntegration.test.jsx show provider/router conventions. React 19 supports title hoisting.
- `frontend/vite.config.mts` has a root package filesystem alias; remove it so the package
  exports map is authoritative. Keep all other aliases/config unchanged. App imports only
  ucm main entry; no charts/chat/markdown optional peers needed; qrcode.react stays required.
- `backend/tests/test_database_driver.py`: assert the configured Django connection vendor is
  PostgreSQL and its Database module is psycopg, without opening a database connection.
- Add brief English developer docs at docs/DEPENDENCIES.md explaining how an app opts into
  dcm extras and re-adds Celery: exact pin, bootstrap celery.py, package __init__ import,
  worker service, settings. Do not add any working Celery runtime scaffolding.

Work from this package; open named files to verify and stay within these seams. Use explicit
UTF-8 for file reads/writes. Never read .env, including names. Application code may load its own
.env as normal; avoid printing sensitive output.

## Preamble and progress contract

The text above is the COMPLETE spec; there is no separate plan to refine. Follow repository
conventions. Do NOT edit MEMORY.md, WORK_ORDERS.md, manifests or lockfiles. Your tools are only
for editing assigned source/test/doc files and running the tests you wrote, once. No dependency
installs, package-manager commands, repo tidying, git add/commit/push, reviews or self-review.
Leave changes uncommitted. Write the required tests and run only your new backend test once
with `python -m pytest tests/test_database_driver.py` from backend if dependencies are ready;
frontend new tests cannot run until Orchestrator installs and runs the package manager, so
report that limitation. The Orchestrator runs the authoritative checks and independent reviews.
State `PLAN: ...` initially, `PROGRESS: [n/total] ...` before relevant actions (no silence over
2 minutes), and exactly one final `RESULT: DONE|BLOCKED <reason>`.

# C. Orchestrator only — NOT ADDRESSED TO THE IMPLEMENTER

> If you are the implementer reading this as your specification: STOP at this line. Everything
> below is the Orchestrator's work. Do none of it; do not launch another implementer.

## Execution directive and authority

Gate #1 is recorded in WORK_ORDERS.md at b2018e7; Part A is unchanged since that commit.
User handover on 2026-10-15 authorizes ucm 4.0.1 instead of Envelope 4.0.0; no other scope change.
Native dispatch requests codex/gpt-6-luna with fresh context. Accepted native agent: /root/wt_orchestrator/wt_implementer, requested model gpt-6-luna, high reasoning, fork_turns=none. Effective provider metadata not exposed.
Native cwd bootstrap exception: inherited workspace root
`C:/Users/Micha Bigler/Documents/webapps`; authorized target is the absolute repo above.
Assigned paths define authority, not technical isolation; native effective provider/containment
metadata are not exposed and remain unverified.

## Verification and independent reviews

Orchestrator owns requirements manifests, package.json, all installs and lockfiles. Preserve
remaining versions. Regenerate pnpm lockfile and resolve backend requirements; no backend
lockfile existed. Run backend affected set including permission and WebSocket inventory,
frontend tests/lint/build, Docker backend_test and final builds where available. CI candidate
ref may prove the actual Linux image/runtime if local Docker is unavailable.
Four configured codex/gpt-6-luna lenses envelope/regression/duplication/tests plus UI and security
review run concurrently on one final immutable diff, read-only and static. Security covers
shared auth dependency behavior and driver/image changes. Fix in-scope findings and re-review.
No prototype exists; title-only replacement changes no layout and needs no visual capture.
Finalize on main only after green required checks/reviews; update register with actual evidence,
commit implementation then register landing SHA in a second documentation commit, push main.


## Execution evidence — 2026-10-15

- Luna completed assigned source/test/doc changes without staging/committing. Its one new-test
  attempt encountered a frontend sandbox EPERM before collection; its backend result was not
  captured. These attempts are not the gate.
- Orchestrator commands from the explicit target working directories: isolated Python
  `-m pytest tests/test_database_driver.py tests/test_requirements_pinned.py
  tests/test_permission_inventory.py backend/test_ws_inventory.py -q`: **12 passed**;
  `node node_modules/vitest/vitest.mjs run`: **5 files, 11 passed**;
  `node node_modules/vite/bin/vite.js build`: passed;
  `node node_modules/eslint/bin/eslint.js .`: zero errors, 20 existing warnings.
- pnpm 11.5.1 regenerated the lockfile and frozen install passed. Existing retained resolved
  versions were preserved. Peer warning is the existing eslint-plugin-react 7.37.5 range versus
  eslint 10.5.0; no related version was changed. The transitive ucm font 5.3.0 is required by
  the published major; the app's existing direct font pin/range is unchanged.
- `docker build -f backend/Dockerfile --target final -t wt-dep-1-final .`: passed, including
  Python 3.14 dependency install, Linux frontend build, collectstatic and final image export.
- Production image smoke via ephemeral `docker run --rm --entrypoint python -e ENV_TYPE=local`:
  Django setup + ASGI import passed; configured driver is psycopg; pytest/Celery/daphne absent.
- Six independent CLI reviews completed concurrently, all banners codex/gpt-6-luna,
  provider openai, sandbox read-only, no bypass: envelope, regression, duplication, tests,
  ui_review, sec_review. Source changes remained immutable during the batch. Some narrow reads
  were blocked by the read-only environment; complete inline diff/context supplied.
- Consolidated findings: **3 raised, 0 accepted, worst accepted none**. Envelope's objection to
  Part B/C is rejected because Orchestrator mapping is mandated and outside implementer
  ownership. Title-test objection is rejected: real pages and actual i18n are rendered, keys
  are unchanged, and wrong production keys fail; changing both the test and production key
  is not a defect in this diff. Driver-test objection is rejected: real Django connection
  proxy is used without mocking, and Database.__name__ == psycopg fails for psycopg2.
  Regression, duplication, UI and security returned no findings.
- Orchestrator targeted security pass: no auth/permission changes, request exposure changes,
  migrations, workflow changes or secret reads. Exact auth transitive pins retained.
- Candidate CI: pending; the final landing register will record its run and reviewed source SHA.
