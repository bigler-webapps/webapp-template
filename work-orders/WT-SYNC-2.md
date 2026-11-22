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
