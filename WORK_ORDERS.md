# WORK_ORDERS.md — webapp-template

Work-order register for this repo. Lightweight directory (not the full orders):
one row per WO with its implementation status. Convention, schema, and maintenance
rules are defined centrally in `webapps/AGENTS.md` → "Work-Order Register".

## Workstream prefixes

| Prefix | Workstream |
|---|---|
| `TPL-*` | Preventive template baseline work inherited by newly scaffolded applications |

Introduce a new prefix when none fits and add it here. New WOs always get a
prefixed ID; never reuse a bare flat number across workstreams.

## Register

| ID | Titel | Beschreibung | Datum | Status | Commit(s) | Notiz |
|---|---|---|---|---|---|---|
| TPL-1 | Bring the template frontend onto the shared theme baseline and current `ui-core-micha` | Adopts `createAppTheme` and its hard completeness assertion, pins the current shared UI package (`2.31.1`), and fixes light-scheme and safe-area handling for every future scaffold. Full spec: [work-orders/TPL-1.md](work-orders/TPL-1.md). | 2026-08-10 | done | bd61e45 | DS-17. One-step dependency bump is deliberate: the assessed intervening releases are feature-only apart from the mail switch, and the template has no onboarding or notification integration that can inherit that default (confirmed by grep — no `Onboarding`/`Notifications`/`browserPush` usage anywhere in the template). The provisional `#FF00FF` accent is intentionally conspicuous and must be replaced by each new app. **Independent `reviewer` (Sonnet) + `ui_reviewer` (Haiku) ran concurrently.** `ui_reviewer`: no findings. `reviewer` found **R1 (P3)** — this row's status used `in review` (space) instead of the schema's hyphenated `in-review`/`done` enum; superseded by this row going straight to `done`. Two things the Orchestrator itself fixed (not reviewer findings, found via the template's own live test run — the mandatory verification step, not a review): (1) Codex bumped `package.json`'s pin but never ran `pnpm install`, leaving `pnpm-lock.yaml` stale at `2.5.0` — installed and re-locked at `2.31.1`. (2) `App.test.jsx`'s mount test asserted `getByRole('heading', {level:1})`, but `Home` renders two `h4`s and no `h1` — a pre-existing heading-level choice unrelated to this WO's scope; the assertion was loosened to `getAllByRole('heading').length > 0` rather than forcing an `h1` into the page. Re-verified: 4/4 scoped vitest tests green, `pnpm lint` 0 errors (18 pre-existing, unrelated warnings). **Two-width rendered side-by-side (DS-1 gate) plus a notched-viewport emulation** (the WO's explicit addition — a standard 375px desktop viewport cannot reveal a safe-area regression) run against the template's own dev server before commit. |
