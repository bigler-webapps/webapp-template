# WORK_ORDERS.md — webapp-template

Work-order register for this repo. Lightweight directory (not the full orders): one row per WO with
its implementation status. The full order lives beside it as `work-orders/<ID>.md`. Convention,
schema and maintenance rules are defined centrally in `webapps/AGENTS.md` → "Work-Order Register".

**Scope note:** this register starts 2026-08-10. Earlier work on this repo is in `git log` — notably
the `CI-*` stream (Dockerfile split, publish-then-pull deploy), which is tracked in
`workflow-templates` and `webapp-management`, not here.

## Workstream prefixes

| Prefix | Workstream |
|---|---|
| `TPL-*` | The template's own frontend and scaffolding surface — what a newly created app inherits |

`TPL-*` was checked estate-wide before being introduced: it is unused in all thirteen existing
registers. It is deliberately not `CI-*`, which already exists in five repos with independent
numbering and therefore forces every cross-reference to name the repo.

| ID | Titel | Beschreibung | Datum | Status | Commit(s) | Notiz |
|---|---|---|---|---|---|---|
| TPL-1 | Bring the template's frontend onto the shared theme baseline, and onto current `ui-core-micha` | The template pins `ui-core-micha` **2.5.0** (current is 2.31.x — 26 minors behind) and hand-rolls `createTheme`, so a newly scaffolded app starts in exactly the pre-baseline state the design-system programme exists to end, and needs an adoption WO on the day it is born. Also fixes two HTML-level defects it would otherwise pass to every future app: a `viewport` meta without `viewport-fit=cover` (inherits jg-ferien's inert safe-area padding) and no declared `color-scheme`. The font loading is already correct and stays. | 2026-08-10 | planned | | Envelope: [work-orders/TPL-1.md](work-orders/TPL-1.md) (Approval Gate #1 pending). The only **preventive** strand in the programme — every other one repairs an existing consumer; this one decides what the fifteenth app inherits. Bump is one step, not two: the operator assessed the 26-minor range as feature-only apart from a well-tested mail switch (2026-08-10). Out of scope and owned by another agent: the template's tooling drift (CI, Dockerfile, `run-dev`/`generate-env`, S112). Program context: `webapp-management/DESIGN_SYSTEM_PROGRAM.md` (DS-17). |
