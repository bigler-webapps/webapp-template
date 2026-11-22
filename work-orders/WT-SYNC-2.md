# WT-SYNC-2 · Bring webapp-template to today's estate standard

## A. Envelope

### Goal & expected outcome

- Goal: an app created from webapp-template today starts with everything the estate expects of a running app, without having to catch up first.
- Expected outcome:
  - current shared-core pins with the settings, URL and frontend wiring those releases require;
  - the standard test scopes, run through `tests.py`;
  - a working isolated acceptance, proven green through `acceptance.py`;
  - current CI action versions;
  - an inventory in Completion that lists every estate change since the last sync and states for each one whether it was adopted, and if not, why.

### Why

- The last substantive template change is WT-SYNC-1 / WT-DEP-1 (2026-10-15). After that only the register (WS-GOV-80/81) and the LF switch (WS-GOV-105) reached the template.
- State on 2026-11-22:

  | Area | webapp-template | Estate |
  |---|---|---|
  | `django-core-micha` | 3.0.0 | 3.41.4 published; apps on 3.40.0-3.41.3 |
  | `@micha.bigler/ui-core-micha` | 4.0.1 | 4.40.0 |
  | `project.yaml` `tests:` scopes (WS-GOV-111) | none | `backend`, `frontend`, a test-management scope |
  | Isolated acceptance (WS-GOV-112/116/121) | none | consumer and adapter, protocol F1-F3, sentinel adapter test |
  | `api/privacy/` route and privacy banner (WS-GOV-113) | none | standard |
  | Workflow actions | `publish-backend-image@v2.13.0` | up to `v2.17.0`; `deploy-app` pinned by SHA |

- Already current, keep as is: the password-reset routes of ui-core-micha, the theme baseline (`createAppTheme`), the JSONL register, LF.
- Operator decisions 2026-11-22 (AskUserQuestion):
  - "Estate-Standard heute";
  - "Ja, lauffähig belegt" for the acceptance;
  - "Direkt auf neueste" for the core pins.

### Scope

1. **Inventory first.**
   - Compare the template against at least two current reference apps that have completed WS-GOV-112, for example kira and kerzenziehen.
   - Also compare against the shared-core changelogs from the template's pins to today:
     - `django-core-micha` `CHANGELOG.md` from 3.0.0;
     - `ui-core-micha` from 4.0.1;
     - `workflow-templates` from v2.13.0.
   - Classify every difference:
     - *adopt*: every new app needs it;
     - *app-specific*: domain code, so skip;
     - *opt-in*: a capability an app enables only when it needs it, such as billing, assistant, messaging channels or receipts. Stays out, with one line naming how an app enables it.
   - The inventory is part of the deliverable.
2. **Core pins.**
   - `django-core-micha` goes to the newest published version at implementation time; `ui-core-micha` likewise.
   - Adopt every change a release requires of a consumer: settings, URLs, migrations, frontend providers.
   - Keep the shared-core defaults, including the allauth security emails (operator 2026-11-22: they stay on).
3. **Test scopes.**
   - Declare `backend`, `frontend` and a test-management scope in `project.yaml`, following the reference apps.
   - Document the canonical `tests.py` and `acceptance.py` calls in `CLAUDE.md`, as the apps do.
   - Keep the existing `test_ws_inventory` and add the permission inventory test the apps carry.
4. **Isolated acceptance, working.**
   - The template carries:
     - a test-management consumer with its settings, URL conf (including `api/privacy/`), Compose file and consumer declaration;
     - an adapter with at least two account templates of different permissions and one synthetic fixture on the template's own models;
     - adapter tests, including the sentinel test per WS-GOV-121 ("Sentinel definition");
     - a committed protocol `work-orders/WT-SYNC-2.acceptance.json` in isolated mode.
   - The protocol criteria:
     - F1: a fixture flow with a synthetic user;
     - F2: two identities in separate sessions, one permitted action, one server-enforced refusal, fixture intact;
     - F3: the central `password_recovery` scenario (WS-GOV-116).
   - Every ID passes through `acceptance.py`.
5. **Privacy.** Add the `api/privacy/` route, plus the privacy provider and banner with the necessary-only default the apps use.
6. **CI.**
   - The workflow action versions and the `app-ci.yml` inputs match the estate standard at implementation time.
   - The template's own `is_template` deploy guard in `main.yml` stays.
7. **Template guidance.** Wherever a new app must replace a template value (names, the fixture, the account templates), the file says so in one comment line.

### Non-goals

- No change to other app repos, `webapp-management-template`, `workflow-templates`, `django-core-micha` or `ui-core-micha`. A gap found in a shared core is reported as a finding, not fixed here.
- No domain features and no opt-in capability enabled by default.
- No change to the deploy guard, and no new deploy target for the template repo.
- No rewrite of the template's existing pages beyond what the pin bumps require.

### Tier · lane

- Tier 3:
  - a shared-core bump that changes or removes things already in use;
  - CI workflow versions;
  - auth-adjacent wiring (password recovery, test-management accounts and permissions).
- The CI part is in the infra lane: the configured implementer writes, security review applies.
- Repo class: template, trunk `main`. The deploy job is skipped on the template repo (`is_template` guard), so a push does not deploy.

### Risks

- 41 minor releases on each core can carry required consumer changes the template misses. The inventory against the changelogs is the safeguard; a missed one shows as a red scope or a failed acceptance ID.
- Template code is copied into every new app. A weak permission check or a test-management route that ordinary settings do not exclude would spread. The tests must prove that ordinary, staging and production settings exclude the test-management routes.
- Reference apps differ. Copying app-specific code into the template would make it heavier. The *app-specific* and *opt-in* classes exist to keep it lean.

### Required tests to WRITE

- Adapter tests: account templates, the fixture, run cleanup and the sentinel test (WS-GOV-121, all four points).
- A settings test: the test-management routes and settings exist only in the test-management configuration, never in ordinary, staging or production settings.
- A permission test for the F2 refusal on the server side.
- A frontend routing test that covers the privacy banner wiring and the reset routes.
- The acceptance protocol with F1-F3, run through `acceptance.py`.

## Gate record

Gate #1 approved by the operator 2026-11-22 (AskUserQuestion: "Freigeben + Übergabetext").

---

## B. Implementation map — filled by the Orchestrator — ADDRESSED TO THE IMPLEMENTER

### Target repo working directory (absolute)

`C:/Users/Micha Bigler/Documents/webapps/webapp-template` (branch `main`, HEAD 37e6117). Write only inside this repo. NEVER edit any other repo; the reference apps below are read-only.

### Context package

Work from this package; do not explore broadly from scratch; open only the named files to verify. If you must dig deeper, use a read-only sub-agent.

**Reference apps (read-only patterns, both completed WS-GOV-112).** Use `Kira` and `innoservice` (kerzenziehen named in Part A has NO adapter yet, so it is not a valid reference; do not use it). Absolute roots `C:/Users/Micha Bigler/Documents/webapps/Kira` and `.../innoservice`.

**Kira files to mirror (template adaptation, not a copy of Kira domain code):**

| Kira path | Template target |
|---|---|
| `backend/backend/test_management_urls.py` | `backend/backend/test_management_urls.py` (include `api/test-management/` + app patterns; keep the `static/` serve line pointing at the frontend build) |
| `backend/backend/test_management_test_settings.py` | same name (adapter unit-test settings: test_settings + `django_core_micha.test_management`) |
| `backend/backend/local_test_management_settings.py` | same name; adapter path `users.test_management.TemplateTestManagementAdapter` |
| `backend/trip/test_management.py` (adapter) | `backend/users/test_management.py` |
| `backend/trip/test_test_management_adapter.py`, `test_test_management_urls.py` | `backend/users/test_test_management_adapter.py`, `backend/users/test_test_management_urls.py` |
| `docker-compose.test-management.yml` | same name at repo root |
| `test-management.consumer.json` | `{"version": 1, "identity": "webapp-template"}`; one comment line cannot go in JSON, so put the "replace identity with your app slug" line in `CLAUDE.md` and `docs/ONBOARDING.md` |
| `frontend/tests/test-management-client.js`, `test-management-controller.js` | same paths; the controller's repo-root search must name `webapp-template` instead of `kira`, and its project regex `^webapp-template-tm-[a-f0-9]{32}$` |
| `frontend/tests/test-management-profiles.spec.js` | F2 spec, same name |
| `work-orders/KIRA-CI-1.acceptance.json` | `work-orders/WT-SYNC-2.acceptance.json` |
| `backend/backend/privacy_manifest.py`, `backend/tests/test_privacy_adoption.py`, `frontend/src/privacy/*`, `frontend/src/__tests__/AppPrivacyRouting.test.jsx`, `frontend/src/components/__tests__/AppShell.privacy.test.jsx` | privacy wiring: manifest (necessary-only default, no optional purposes registered by the template), `api/privacy/` route, provider + banner in `App.jsx`/`index.jsx` |
| `backend/backend/settings.py`, `urls.py`, `test_settings.py`, `backend/tests/test_security_settings.py`, `test_ws_inventory.py`, `test_permission_inventory.py`, `project.yaml` `tests:` block, `.github/workflows/*.yml`, `backend/conftest.py`, `backend/pytest.ini`, `frontend/vitest.config.js`, `frontend/package.json` scripts | diff each against the template file and adopt only what a NEW app needs |

**Template models and permissions** (verified): `users.UserProfile` (role in `ROLE_DEFINITIONS`: none 0, collaborator 1, supervisor 2, admin 3, `settings.py:44`), `users.AuthPolicy`, `utils.PrivacyStatement`, `utils.CookieStatement`. API: `api/users/` is `users.views.UserViewSet(BaseUserViewSet)` (permission rules live in `django_core_micha.auth`; read them, do not change them). `INVITE_MIN_ROLE_LEVEL = 2`. There is no domain model; do NOT add a model or a migration for the fixture.

**Adapter design (binding):**
- Two account templates of different permissions: `supervisor` (UserProfile role `supervisor`) and `collaborator` (role `collaborator`). Set the role through the profile that the `post_save` receiver creates (`users/models.py:16`); `effective` reports it.
- One synthetic fixture on the template's own models: `managed-user` = a run-owned synthetic user row with a profile (role `none`), parameterised by the supervisor account, marked with a run-handle marker in its username, recorded in `adapter_state`. No new table.
- F2 behaviour: a permitted action for the supervisor and a server-enforced refusal for the collaborator against that fixture on `api/users/`. Read `BaseUserViewSet` to choose a real permitted/refused pair (for example list/retrieve versus an invite or role change guarded by `INVITE_MIN_ROLE_LEVEL`); state which pair you used in the spec's first comment line. The refused action must leave the fixture row unchanged (assert it).
- Cleanup (`reset_run`, `close_run`) deletes only run-owned rows verified by marker and the `Collector` allow-list (Kira pattern, allow-list: `auth.user`, `users.userprofile`, `account.emailaddress`, `account.emailconfirmation`, plus any other label you can show the template creates; fail closed otherwise). Sessions of run users are removed.
- Sentinel test per WS-GOV-121, all four points (`work-orders/WS-GOV-121.md` lines 21-28): outside the run create an ordinary user with profile + `EmailAddress` + a logged-in session, plus a row of every model the cleanup deletes or modifies (user, profile, email address, the fixture's user type); run account creation, fixture preparation, then BOTH `reset_run` and `close_run`; assert every sentinel row and its field values unchanged and the sentinel session still present; assert the run's own rows and sessions are gone.
- Settings test (required): ordinary, staging and production settings (`backend.settings` with `ENV_TYPE` local/staging/production variants, and `backend.test_settings`) must NOT contain `django_core_micha.test_management` in `INSTALLED_APPS`, must not set `TEST_MANAGEMENT_ENABLED`, and `reverse`/URL resolution of `/api/test-management/` must 404 under their URL conf. Prove the positive case only under the dedicated test-management settings. Mirror `Kira/backend/tests/test_security_settings.py` and `innoservice`'s equivalent.
- Permission test (required): server-side refusal for the collaborator on the F2 action using DRF `APIClient`, fixture unchanged afterwards; extend `backend/tests/test_permission_inventory.py` only if the inventory needs the new route (it should not: the test-management URLs exist only in the dedicated URL conf).

**Frontend:** add the privacy provider and banner exactly as Kira/innoservice wire it with the ui-core-micha version you pin (read ui-core `CHANGELOG`/exports for the privacy exports; do not guess names). Required frontend tests: a routing test covering the privacy banner wiring and the reset routes (`/reset-request-password`, `/reset/:uid/:token`, `/invite/:uid/:token`), added to the existing `frontend/src/App.test.jsx` / `AuthRoutesIntegration.test.jsx` or a new behaviour-named file. The template's reset-request route is `/reset-request-password`: in the acceptance protocol F3 set `"routes": {"reset_request": "/reset-request-password"}`.

**Acceptance protocol (`work-orders/WT-SYNC-2.acceptance.json`):** `mode: isolated`, `controller_module: frontend/tests/test-management-controller.js`; actors `supervisor` and `collaborator` plus F1 fixture `managed-user`; criteria exactly F1 (`WT-SYNC-2-F1`, actor supervisor, fixture, route that shows the user list, visible check plus an `api_expect` on `api/users/` that finds the fixture marker), F2 (`WT-SYNC-2-F2`, `spec` = the profiles spec), F3 (`WT-SYNC-2-F3`, `scenario: password_recovery`, template `supervisor`, `locale: de-CH`, routes as above). Put F3 last. Validate shape against the `acceptance.py` docstring (`C:/Users/Micha Bigler/Documents/webapps/.claude/scripts/acceptance.py`, read-only) and the Kira file.

**`project.yaml` `tests:` block:** scopes `backend`, `backend_test_management`, `frontend`, same shape as Kira (`docker exec <prefix>_local-backend-1 ...`, frontend `node node_modules/vitest/vitest.mjs run` with `cwd: frontend`). The template's `container_prefix` is a placeholder: write the prefix literally as `webapp-template` and add ONE comment line "replace webapp-template with your container_prefix". Do not change the other placeholders in `project.yaml`.

**Inventory (part of the deliverable):** write `work-orders/WT-SYNC-2.inventory.md` (the Orchestrator folds it into `## Completion`). Sources: the Kira and innoservice trees, `django-core-micha/CHANGELOG.md` from 3.0.0 to 3.41.4, `ui-core-micha/CHANGELOG.md` from 4.0.1 to 4.40.0, `workflow-templates/CHANGELOG.md` (or its tags/docs) from v2.13.0 to v2.17.0. Table columns: `Change | Source (release or reference file) | Class (adopt / app-specific / opt-in) | Status (adopted in <file> / skipped) | Reason or "enable by:" one line`. Every consumer-required change of a release (settings key, URL include, migration, frontend provider/export, removed or renamed export) must appear. Read changelogs by range with `Grep -n`, never whole.

**Core pins (you edit the declarations; you do NOT install):** `backend/requirements.txt` `django-core-micha==3.41.4` (re-check the top entry of `django-core-micha/CHANGELOG.md`; if a newer one exists, use it and say so). `frontend/package.json` `@micha.bigler/ui-core-micha` to `4.40.0` (same re-check on `ui-core-micha/package.json` `version`, currently `4.40.0`). Do NOT edit `frontend/pnpm-lock.yaml`; the Orchestrator regenerates it. Keep allauth security emails at the shared-core defaults. If a core release requires a new Python/JS dependency in `requirements.txt`/`package.json`, add it with an exact pin (`test_requirements_pinned.py` enforces `==`) and list it in the inventory.

**CI:** update `.github/workflows/ci.yml`, `main.yml`, `staging-health.yml` action refs and `app-ci.yml` inputs to what `Kira/.github/workflows/*.yml` use today (workflow-templates `v2.17.0`; `deploy-app` pinned by the same SHA Kira uses). KEEP the `is_template` deploy guard in `main.yml` and the `.github/scripts/test_ci12_deploy_workflow.py` check passing; update that script only if the guard text it matches moves, and say so. No new deploy target. This part is infra-lane: do not alter permissions blocks beyond what the Kira workflow files show.

**Template guidance:** every value a new app must replace (identity in `test-management.consumer.json`, container prefix in `tests:`, fixture name/adapter, account templates) gets one comment line in the file (Python/YAML/compose/JS) or one bullet in `docs/ONBOARDING.md` for JSON; add the canonical `tests.py` / `acceptance.py` calls to `webapp-template/CLAUDE.md` (copy wording from `Kira/CLAUDE.md`/`innoservice/CLAUDE.md` if present; otherwise one short section: `python -I .claude/scripts/tests.py --repo <repo> [--scope backend|backend_test_management|frontend]` and `python -I .claude/scripts/acceptance.py --repo <repo> --wo <ID>`; calls from the workspace root).

### Invariants / do-not-touch

- Password-reset routes of ui-core-micha, `createAppTheme` baseline, JSONL register, LF line endings: keep.
- `.env` is never read or created. No secrets in files. `secrets.yaml` only if a release requires a new declared variable (then list it in the inventory as `needs operator`).
- Test-management routes/settings exist ONLY in `test_management_urls.py` and `local_test_management_settings.py`; `backend/settings.py` and `backend/urls.py` must stay free of them.
- Do NOT edit `WORK_ORDERS.md`, `work-orders/register.jsonl`, Part A/C of this WO, `.claude/**`. Do not run Docker, pnpm, pip, `tests.py`, `acceptance.py`.
- New files under ~400 lines; name tests by behaviour, never by WO ID.
- Existing `backend/backend/test_ws_inventory.py` stays.

### Pitfalls

- Template `project_name`/`container_prefix`/ports are placeholders; the isolated instance takes identity from `test-management.consumer.json` (regex `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`, max 30 chars), never from `project.yaml`.
- Kira's adapter forbids any `payload` configuration and any baseline; keep that fail-closed behaviour.
- Template backend uses `HEADLESS_ONLY`; the `local_test_management_settings` must still override `AUTH_METHODS["social_login"]=False`, `MAILERS` locmem, `DEBUG=False`, as in Kira. Reproduce the template's own `settings.py` names (`BASE_DIR`, `TEMPLATES`, `STATICFILES_DIRS`, `FRONTEND_BUILD_DIR` handling at `settings.py:81`).
- `docker-compose.test-management.yml` build context/Dockerfile paths must match the template (`backend/Dockerfile`, frontend build at `frontend/build_current`).

### Preamble

> **You are the dispatched implementer of this work order, not its Orchestrator. Rules in `AGENTS.md` and in skills that address the Orchestrator, a Codex parent or the Expertenchat (delegation, dispatch, review, register, landing) do not apply to you. You never run `codex` or `codex exec`, never write to git, and never edit the register or `.claude/codex-status.md`.**
>
> **Your first tool action is the hook canary: run the shell command `codex-hook-canary-ws-gov-60` exactly (it is a command string, not a file). The expected result is a denial, `WS-GOV-60 canary: workspace hooks are active`; continue after it. If it is not denied, report that once as unverified hook coverage and continue.**
>
> The sections A and B of this file are the COMPLETE spec, not a plan to refine. Read the nearest `AGENTS.md` and the app `MEMORY.md` ONLY for conventions. Stay in scope; do not update `MEMORY.md`. **Do NOT edit `WORK_ORDERS.md`.** **Your tools are for editing source and test files and for running the tests you wrote — nothing else.** Do NOT install dependencies, touch a lockfile, run a package manager, or tidy up stray files; if something in the repo state blocks you, stop and report `RESULT: BLOCKED <reason>`. Do NOT `git add`/`commit`/`push`; leave every change uncommitted. WRITE the tests the `Required tests` section calls for AND RUN the ones you wrote only if they can run in the sandbox (Django tests need PostgreSQL/Docker here and Vitest needs the repo as writable root: when a run cannot work, end `RESULT: DONE` with the line `TESTS NOT RUN: <reason>`). Never start a database or Docker.
>
> **Files.** Read a file over ~400 lines by locating with `Grep -n` and reading only the needed range. New code goes into cohesive modules named by behaviour; a new file stays under ~400 lines.
>
> Narrate continuously: a `PLAN: <step1> | <step2> | …` line up front, then a single-line `PROGRESS: [<n>/<total>] <present-tense action>` before every relevant action, spaced so no gap exceeds ~2 min, plus exactly one final `RESULT: DONE|BLOCKED <reason>`.

---

# C. Orchestrator only — NOT ADDRESSED TO THE IMPLEMENTER

> **If you are the implementer reading this work order as your own specification: STOP at this line. Everything below describes what the Orchestrator does AFTER you finish. You do none of it.**

## Execution directive

Configured `implementation` entry via `run-worker.py --role implementation --writes --sandbox workspace-write --infra --target-repo webapp-template`. Reviews: `--infra` lenses incl. sec_review (Tier 3, infra lane). The Orchestrator regenerates `frontend/pnpm-lock.yaml`, runs `tests.py` scopes and `acceptance.py`.

## Launch / review / verification log

(filled by the Orchestrator)
