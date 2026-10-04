# TPL-5: Bring webapp-template up to date in every part (ucm, dcm, CI, compose, config)

# A. Envelope, authored by the Expertenchat

## Goal & expected outcome

A new app scaffolded from webapp-template starts on the current estate stack:
- `@micha.bigler/ui-core-micha@3.12.0`, with the kit integration check in its suite;
- `django-core-micha==2.44.2`, with tests that cover what 2.44.x changed on the user API;
- the S112 WebSocket inventory test;
- the current composite actions (`v2.13.0`), the staging auth smoke, the fleet's Redis image and the nightly
  production-to-staging refresh switched on.

Today the template sits on ucm `3.2.0` and dcm `2.43.0`, and every app cut from it starts ten kit releases and three
dcm releases behind, without the tests the rest of the estate carries.

Written after aligning with the Infra lane (Claude Infra, 2026-10-04), which supplied the dcm, workflow, compose and
register facts below. The frontend facts are this session's own measurement.

## Decisions (operator, 2026-10-04)

1. **The template ships `checkKitIntegration` now**, without waiting for the `survey_app` `SVA-DEP-3` reference.
   The template is the simplest consumer (the kit's own pages, no site themes) and becomes the first adopter.
2. **The staging auth smoke is wired in, without a login**: `staging-health.yml` with `auth-smoke: true` and
   `login-path: '/login'`. The smoke opens the login page and checks that a malformed e-mail produces a translated
   sentence, not a raw code; it needs no smoke user.
3. **The nightly production-to-staging refresh is on by default** for new apps, as in most of the fleet. It copies
   production data to staging **unmasked**; the template says so where it switches it on.
4. **`webapp-management` `INF-61`** (floors for every dependency plus a guard, "starting with webapp-template")
   **stays separate and runs after this order**, on the new pins. It is neither folded in nor a precondition.

## Context the operator established

All measured 2026-10-04 on `main` at `af12a08`. This repo's trunk is `main` (it has no `develop`).

### Frontend (ucm)

- **Pin:** `frontend/package.json` `"@micha.bigler/ui-core-micha": "3.2.0"` (`INF-64`), `pnpm@11.5.1`, one `i18next`
  (26.3.1).
- **What the template takes from the kit:** `AuthProvider`, `AuthContext`, `LoginPage`, `SignUpPage`,
  `SignupConfirmPage`, `PasswordInvitePage`, `PasswordResetRequestPage`, `AccountPage`
  (`src/pages/AccountHubPage.jsx:13`, without props), `ProfileComponent`, `updateUserProfile`, `WidePage`,
  `createAppTheme` (`src/theme.js`), `uiCoreTranslations` (`frontend/i18n/index.js`). Routes `/login`, `/signup`,
  `/signup/confirm`, `/invite/:uid/:token` in `src/App.jsx`. Providers: `ThemeProvider` in `src/index.jsx`,
  `AuthProvider` in `src/App.jsx`. No kit chart, no kit messaging.
- **What changes from 3.2.0** (`ui-core-micha/CHANGELOG.md`; the kit's runtime and peer dependencies are unchanged):
  - `3.12.0` / `UCM-THEME-18`: the new type scale (h1-h3 36/32/28, h4 24 and 23 below `sm`, h5 20, subtitle1 13;
    value source `ui-core-micha/docs/TYPE-SCALE.md`). The template's headings are already role-correct (h4 titles at
    `src/pages/Home.jsx:20` and `WelcomePage.jsx:43`, no h5), so no app code moves.
  - `3.11.x`: dark-mode capability in `createAppTheme` (unused here; light output unchanged), translated
    pagination, the QR info box ground.
  - `3.10.0` / `UCM-TEST-1`: `checkKitIntegration({ i18n, wrapper, pages })`, which returns `{ findings }`. It checks
    that every kit key exists in each shared language, that the app's i18n **is** the initialised default instance
    (otherwise `Accept-Language` is missing), that the kit pages render inside the app's providers, and that a
    malformed-email login shows the translated sentence. It stubs `apiClient`'s adapter itself.
  - `3.9.1` / `UCM-AUTH-11`: no self-delete button for an administrator in `UserListComponent`.
  - `3.9.0` / `UCM-AUTH-10`: translated error resolution; `Accept-Language` on every kit request; kit components
    call `useTranslation()` for `t` and `i18n`.
  - `3.8.0` / `UCM-THEME-15`, `3.7.0` (`UCM-AUTH-9`, `UCM-I18N-4`, `UCM-SHELL-7`, `UCM-PRIM-2`), `3.6.0` / `AUTH-8`,
    `3.5.1` / `AUTH-7`, `3.5.0` / `MSG-19`, `3.4.0` / `AUTH-6`, `3.2.1`-`3.3.1` (charts): auth error handling and
    additive pieces; the charts and messaging entries do not touch the template.
- **Tests today:** `src/App.test.jsx` (theme built by `createAppTheme`, no completeness findings, the deliberate
  `#FF00FF` placeholder accent). No route-integration test, no kit integration check. No file mocks `react-i18next`.

### Backend (dcm)

- **Pin:** `backend/requirements.txt:3` `django-core-micha==2.43.0`, `Django==6.1` (stays). `2.44.2` is on PyPI
  (checked 2026-10-04).
- **What changes from 2.43.0** (from the Infra lane):
  - `2.43.1`: `run-dev` `--refresh-deps`; `--no-log-stream` ends with one `READY <url>` or `TIMEOUT` line. No app change.
  - `2.43.2` / `DCM-NOTIF-10`: notifications gain `resolved_at` and a partial unique constraint; dcm's own migration
    `0009` runs on migrate.
  - `2.44.0` / `DCM-AUTH-1`: invite links valid 30 days; optional setting `INVITE_LINK_TIMEOUT_DAYS`.
  - `2.44.1` / `2.44.2` / `DCM-AUTH-2`, `-3`, **behaviour change on an auth surface**: through the generic user routes
    of `BaseUserViewSet`, a non-admin can no longer PATCH fields outside the allowlist or DELETE their own row
    (403); other rows are unchanged.
- **The template exposes the user viewset:** `backend/users/views.py:10` `UserViewSet(BaseUserViewSet)` widens
  `current_patch_allowed_fields` with `is_new` (`:13`), routed in `backend/users/urls.py:10`.
  `backend/users/tests.py` is empty (three lines).
- **WebSocket inventory (S112):** the template installs `django_core_micha.notifications` (from dcm's
  `settings_base`), whose `consumers` module exists, while `backend/backend/routing.py` registers no WebSocket
  route. There is no `test_ws_inventory`; `AGENTS.md` -> S112 requires one in every app's suite.
  `backend/tests/test_permission_inventory.py` exists. Model: `spesix/backend/backend/test_ws_inventory.py`.

### CI, compose and config

- **Composite actions:** `.github/workflows/main.yml:47` `publish-backend-image@v2.9.0`, `:53` `deploy-app@v2.9.0`.
  The current `workflow-templates` tag is `v2.13.0`; between `v2.9.0` and `v2.13.0` both actions gained only
  optional inputs (survey-specific Vite build args on `publish-backend-image`; `CHANGELOG.md` read 2026-10-04).
- **Reusable workflows stay on `@main`** (`ci.yml:14`, `staging-health.yml:15`): decided 2026-10-03 (`WS-GOV-15`,
  `KZ-CI-2` dropped). `staging-health.yml` keeps its `if: ! github.event.repository.is_template` guard.
- **Auth smoke inputs** (`workflow-templates` `staging-health.yml`): `auth-smoke` (boolean, default off) and
  `login-path` (default `/login`). `WFT-CI-31` is done; no app has opted in yet.
- **Redis:** `docker-compose.yml:113` `redis:alpine`; `docker-compose.local.yml:28` already `redis:8-alpine`, as the fleet
  settles on.
- **Refresh opt-in, two halves** (`spesix/project.yaml:18`, `spesix/docker-compose.yml:81-84`):
  `staging_refresh: true` in `project.yaml`, and the label `"dbrecv.enable=true"` on the `db` service, with the
  comment that an authorisation decision about production data belongs in a reviewed diff. The template has
  neither (`docker-compose.yml:99-102` carries only the `backup.*` labels).
- **Measured, no change:** `secrets.yaml`, `project.yaml` and `monitoring/` against kerzenziehen and spesix differ
  only by app-specific keys (`EMAIL_PASSWORD`, `OPENAI_*`, `deploy_target`, `version`, `root_module`); `renovate.json`
  is already the `CI-7` form; Postgres is `postgres:18` with the PG18 mount.

### Registers

- `webapp-management` `INF-38` (in progress, the old ucm `2.41.3` catch-up) is superseded **for the template** by this
  order's `3.12.0` pin; the template drops out of it.
- **The nightly refresh is live.** `webapp-management` `refresh-staging.yml` is green for the opted-in apps (scheduled
  runs 2026-09-30 to 10-02; on 10-03 and 10-04 only the research-prod/hram leg failed, fixed by `WM-CI-25` and
  proven by run `37213361336`, checked 2026-10-04). `CI-13`'s row is still in progress, but the mechanism it describes
  is what the workflow already runs. A new app is included through exactly the two halves this order ships:
  `staging_refresh: true` (read by `resolve_daily_refresh_matrix` via the app registry) and `dbrecv.enable=true` on
  `db`. Corrected 2026-10-04 on the Infra lane's word: the first version of this order called `CI-13` a nightly
  failure risk, which it is not.

## Scope + non-goals

In scope:
- **Frontend:** the ucm pin -> `3.12.0` and the regenerated lockfile; a kit integration test; a route-integration
  test.
- **Backend:** the dcm pin -> `2.44.2`; user-API tests for the 2.44.x behaviour; a WebSocket inventory test.
- **CI and compose:** both composite actions -> `v2.13.0`; `auth-smoke: true` and `login-path: '/login'` in
  `staging-health.yml`; `redis:8-alpine` in `docker-compose.yml`; `staging_refresh: true` in `project.yaml` and
  `"dbrecv.enable=true"` on the `db` service, each with a comment that names the unmasked copy of production data.

Non-goals:
- **The E2E harness.** "Joined" is per app (seed, specs, manifest, three green CI runs). The dcm/ucm extraction of
  its common parts comes first (`WS-GOV-1` follow-up); the template adopts those pieces afterwards.
- `INF-61` (dependency floors and guard): separate, after this order.
- No dark mode switched on, no theme or accent change, no app code change for the type scale.
- No change to `secrets.yaml`, `monitoring/`, Traefik labels, `renovate.json` or the reusable-workflow refs.
- No other dependency change; no Django change.

## Tier · precondition / gate

- **Tier 3 · tests: the kit integration and route-integration tests (new); the user-API and WebSocket inventory
  tests (new); `src/App.test.jsx`, `backend/tests/test_permission_inventory.py`; the template's full frontend and
  backend suites in CI (dependency-bump exception, named).** Dependency bumps that change behaviour on auth
  surfaces, a CI workflow change, and a default that moves production data (`AGENTS.md` -> Tiering).
- Preconditions, met 2026-10-04: `ui-core-micha@3.12.0` and `django-core-micha==2.44.2` published; `workflow-templates`
  `v2.13.0` tagged.

## Risks

- **The template cannot exercise its own staging wiring.** `staging-health` is skipped on the template repo, so the
  auth smoke and the refresh first run on the first scaffolded app. The order ships them correct by reading, and
  says so.
- **First adopter of `checkKitIntegration` and of the auth smoke.** A defect in either surfaces here first; it is
  fixed in the kit or in `workflow-templates`, never worked around in the template.
- **The refresh copies production data unmasked** to staging, by operator decision, as the fleet does.
- **Manifest bumped, lockfile stale**, the known trap of every bump.

## Required tests to WRITE (you write them and run YOUR OWN new ones; the Orchestrator's run is the gate)

Frontend (`vitest run`):

1. **Kit integration check.** `checkKitIntegration({ i18n, wrapper })` with the template's own i18n
   (`frontend/i18n/index.js`) and a wrapper that applies the template's own providers (theme and auth, as in
   `src/index.jsx` and `src/App.jsx`) returns `{ findings: [] }`.
2. **Route integration.** Inside the template's providers, `/signup` renders the kit's `SignUpPage` and
   `/invite/<uid>/<token>` renders `PasswordInvitePage` without throwing. Mock only the network, never the kit
   components. (Pattern: `survey_app/frontend/src/AuthRoutesIntegration.test.jsx`.)

Backend (`pytest`):

3. **User API, own row, as a non-admin:** PATCH of `is_new` (the template's allowlisted field) succeeds; PATCH of a
   field outside the allowlist is refused (403); DELETE of the own row is refused (403).
4. **WebSocket inventory (S112):** `assert_all_consumers_secure(["django_core_micha.notifications.consumers"]) == []`,
   with the comment that every new consumer module is added there. Model: `spesix/backend/backend/test_ws_inventory.py`.

Run, do not write: `src/App.test.jsx`, `backend/tests/test_permission_inventory.py`, and both suites.

## Acceptance

1. `frontend/package.json` and the lockfile resolve `@micha.bigler/ui-core-micha@3.12.0`, with a single `i18next`;
   `backend/requirements.txt` pins `django-core-micha==2.44.2`.
2. The new tests and both suites pass in CI.
3. `main.yml` uses `v2.13.0` for both actions; `staging-health.yml` passes `auth-smoke: true` and `login-path: '/login'`;
   `docker-compose.yml` runs `redis:8-alpine` and labels `db` with `dbrecv.enable=true`; `project.yaml` sets
   `staging_refresh: true`.
4. No manual walk-through: the template has no deployment.

## Parity guardrail

No behaviour change in template app code. The pins, the lockfile, the named workflow, compose and config lines with
their comments, and the four new tests.

---

# B. Implementation map, filled by the Orchestrator and ADDRESSED TO THE IMPLEMENTER

## Context package

The pins, lockfile, CI, compose and config changes are ALREADY DONE (Orchestrator). Your job is the four new tests only. Do not explore broadly; open only the named files.

- **Test 1 (kit integration), new file `frontend/src/kitIntegration.test.jsx`.** Use `checkKitIntegration` from `@micha.bigler/ui-core-micha` (README "Consumer integration check"): `const { findings } = await checkKitIntegration({ i18n, wrapper })`, expect `findings` toEqual `[]`. `i18n` is the default export of `frontend/i18n/index.js` (import it as `../i18n/index.js`; `src/i18n.js` re-exports it). The `wrapper` is a component applying the template's providers: `ThemeProvider` with `theme` from `src/theme.js` plus `AuthProvider` from the kit (see `src/index.jsx`, `src/App.jsx`; the router comes from the kit's check, do not add one unless it demands it). Set `globalThis.IS_REACT_ACT_ENVIRONMENT = true` if the check needs it. Run this check alone in its own test file (it stubs `apiClient`'s adapter).
- **Test 2 (route integration), new file `frontend/src/AuthRoutesIntegration.test.jsx`.** Model: `survey_app/frontend/src/AuthRoutesIntegration.test.jsx` (read-only sibling; mock `axios` with `vi.hoisted` axios instance, `vi.mock("./components/Header", ...)` to null). Render `<App />` at `/signup` and `/invite/some-uid/some-token` (`window.history.pushState`), `waitFor` a real `form` element in the container. Wrap in `ThemeProvider` with `theme` from `./theme` and import `./i18n`. Mock only the network, never kit components.
- **Test 3 (user API), edit `backend/users/tests.py`** (currently empty; it is in `pytest.ini` testpaths). View: `backend/users/views.py:10` `UserViewSet(BaseUserViewSet)` with `current_patch_allowed_fields` widened by `is_new`; routed via `backend/users/urls.py` (router prefix `""`, basename `user`). Find the mount prefix in `backend/backend/urls.py`, and read `django_core_micha/auth/views.py` (`BaseUserViewSet`, `current_patch_allowed_fields`, and the detail-route PATCH/DELETE logic of dcm 2.44.2 installed in the backend environment) to determine the exact URL for the own-row detail route. Use DRF `APIClient` with `force_authenticate` as a NON-admin user created with `get_user_model()` (email-based, check `backend/backend/settings.py` for the user model fields). Assertions: PATCH own row `{"is_new": false}` succeeds (2xx and field persisted, via whichever route dcm exposes for the own row, e.g. the "current" action); PATCH of a field outside the allowlist (use a field the serializer in `backend/users/serializers.py` exposes, e.g. `is_staff`/`email` as present) is refused with 403 via the generic detail route; DELETE of the own row is refused with 403. Use `@pytest.mark.django_db`. If the real response differs from the Envelope (e.g. 400 vs 403), report `RESULT: BLOCKED` with the measured value rather than weakening the test.
- **Test 4 (S112), new file `backend/backend/test_ws_inventory.py`**, copy of `spesix/backend/backend/test_ws_inventory.py` (read-only sibling): `assert_all_consumers_secure(["django_core_micha.notifications.consumers"]) == []`, docstring noting every new consumer module is added there. Also add `backend/test_ws_inventory.py` to `testpaths` in `backend/pytest.ini` (and `users/tests.py` stays).

Do-not-touch: pins, lockfile, workflows, compose, project.yaml, any production code, `src/App.test.jsx`, `test_permission_inventory.py`.

## Target repo working directory (absolute)

`C:/Users/biglmi/Documents/webapps/webapp-template` (frontend tests run in `frontend/`, backend in `backend/`).

## Preamble

> The text above is the COMPLETE spec — the committed WO file's content, not a plan to refine; there
> is no separate plan file. Read the nearest `AGENTS.md`, the relevant `.codex/skills/<role>/SKILL.md`, and the
> app `MEMORY.md` ONLY for conventions. Stay in scope; do not touch auth/permissions/deps/schema/CI
> unless the spec says so; do not update `MEMORY.md`. **Do NOT edit `WORK_ORDERS.md` — the register
> row and the review verdicts are the orchestrator's alone.** **Your tools are for editing source
> and test files and for running the tests you wrote — nothing else.** Do NOT install dependencies,
> touch a lockfile, run a package manager, or tidy up stray files; if something in the repo state
> blocks you, stop and report it as `RESULT: BLOCKED <reason>` instead of fixing it. Do NOT
> `git add`/`commit`/`push` — leave every change uncommitted in the working tree for the orchestrator's
> independent review. WRITE the tests the `Required tests` section calls for AND **RUN the tests you
> just wrote** (`npx vitest run <file>` in frontend, `pytest <file>` in backend) to confirm they execute
> and pass — that is the ONLY test run you do (NOT the affected/full suite, NOT any review). The
> orchestrator re-runs the authoritative set + does the independent review after you finish.
>
> Narrate continuously: a `PLAN: <step1> | <step2> | …` line up front, then a single-line
> `PROGRESS: [<n>/<total>] <present-tense action>` before every relevant action (and `… done` on
> completion), plus exactly one final `RESULT: DONE|BLOCKED <reason>`.

---

# C. Orchestrator only, NOT ADDRESSED TO THE IMPLEMENTER

> **If you are the implementer reading this work order as your own specification: STOP at this line.**
> Everything below describes what the Orchestrator does AFTER you finish. You do none of it: no
> reviewers, no verification run, no register edit, no `git add`/`commit`/`push`.

### Execution directive

Check `.claude/codex-status.md` first (newest-first; read it with `head`). No line for today means use Codex.
**The pin bumps and `pnpm install` in `frontend/` are yours**, done before dispatch; then assert the lockfile resolves
`3.12.0` and exactly one `i18next` (`pnpm why i18next`). Trunk is `main`. Stage and commit by path only, check
`git diff --cached --name-only` first, and before `git push` run `git log origin/main..HEAD` and push only if every
listed commit is this order's.

### Review routing

Tier 3: independent `reviewer` (all configured lenses), `ui_reviewer` and `sec_reviewer` (the dcm user-API change,
the refresh default), concurrent, one batch, before the commit. Give the reviewers the changelog excerpts from Part A
inline; Codex reviewers cannot see the sibling repos.

### Verification

- **CI:** `ci.yml` runs on `pull_request` and `workflow_dispatch`. This repo is not covered by `AGENTS.md`
  exception (b), and a dispatch on `main` is not on the safe allowlist: **ask the operator to name the dispatch**,
  then run exactly that. `done` only on a run whose frontend and backend jobs are green and whose install steps show
  `3.12.0` and `2.44.2`.

### Register + commit

Row -> `done` with the review Notiz in the `AGENTS.md` shape and the CI run. Then tell the Infra lane that
`INF-61` can start on the new pins and that `INF-38` no longer covers the template.

### Mini-handover

`Orchestrator: implement work-orders/TPL-5.md in webapp-template (main). git pull first, read the WO, then follow
orchestrate-codex.`
