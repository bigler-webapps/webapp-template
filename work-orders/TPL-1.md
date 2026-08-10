# TPL-1 — Bring the template's frontend onto the shared theme baseline, and onto current `ui-core-micha`

**Target repo:** `webapp-template` (branch `main` — only branch)
**Tier:** 2 — a dependency bump, and `deps/CI` is in AGENTS.md's Tier-2 forcing list
**Review:** independent `reviewer` **and** `ui_reviewer` — spawned concurrently, both mandatory before commit
**Decision record:** `webapp-management/DESIGN_SYSTEM_PROGRAM.md` (DS-17)
**Prefix note:** new `TPL-*` prefix, checked estate-wide as unused across all thirteen registers. Not `CI-*` — that prefix already exists in five repos with independent numbering, which forces every cross-reference to name the repo.

---

## A. Envelope

### Goal

A newly scaffolded app should start **correct**, not need an adoption work order on the day it is
born. Bring the template's frontend onto `createAppTheme` and onto current `ui-core-micha`, and fix
the two HTML-level defects it would otherwise pass on to every future app.

### Why this one is different from every other strand

Every other item in the design-system programme is **remedial** — it repairs one of the 14 existing
consumers. This one is **preventive**: the template decides what the fifteenth app inherits. It is the
only change that stops new debt instead of paying down old debt, and it is why it sits on the critical
path rather than in the demand-driven backlog.

### Measured evidence (2026-08-10)

| | `webapp-template` today | |
|---|---|---|
| `ui-core-micha` pin | **`2.5.0`** | current published is 2.31.x — **26 minors behind** |
| `frontend/src/theme.js` | hand-rolled `createTheme`, 2.3 kB | exactly the pre-baseline pattern the programme exists to end |
| `viewport` meta | `width=device-width, initial-scale=1` — **no `viewport-fit=cover`** | inherits jg-ferien's defect: `env(safe-area-inset-*)` resolves to zero |
| `color-scheme` | not declared in `App.css` or `index.css` | browsers may paint native form controls from their dark palette |
| Font loading | `@fontsource/dm-sans`, scoped latin subsets | **already correct** — no CDN, unlike spesix. Leave it alone. |

A scaffolded app therefore begins with a hand-rolled theme, a 26-minor gap, and two latent defects.

### Scope

#### A. Bump `ui-core-micha` to the then-current published version

- Bump from `2.5.0` to whatever is published when this WO runs — do **not** hardcode `2.31.0` here;
  `THEME-2` may have landed a patch by then. Read the published version and pin it exactly, as every
  other consumer does.
- **One step, not two, and here is why:** DS-10's equivalent bump (five minors) is deliberately split
  from its theme rewrite so a regression stays attributable. The operator assessed this 26-minor range
  on 2026-08-10 as **feature-only apart from a well-tested mail switch**, with nothing requiring
  investigation. Recorded as the *reason* the split was skipped, so a later reader sees a decision
  rather than an oversight.
- **The mail switch deserves one glance at scaffold level.** If it changed a default, a scaffolded app
  inherits the new one — so confirm the template's own config carries the intended value. One check,
  not an investigation.

#### B. `theme.js` → `createAppTheme`

Replace the hand-rolled `createTheme` call with the factory. The template's `theme.js` should end up
being what an adopting app's becomes: the palette and the font, nothing else.

**The one real decision in this WO — the placeholder accent.** `createAppTheme` throws without
`palette.primary` (decision 21), so the template *must* ship one, and whatever it ships is copied into
every future app. This is the exact hazard behind rejecting a neutral fallback in decision 21, arriving
through the template instead.

**Recommendation: a visibly provisional value** — a colour no product would ship (e.g. `#FF00FF`) with
an adjacent `// TODO: replace with this app's accent` comment. A plausible grey or blue would survive by
inertia and two apps would silently look alike; a garish one makes a fresh scaffold obviously unfinished,
which is the intended signal. **The operator may overrule this at Gate #1** — it is a taste call with a
real downside (a freshly scaffolded app looks broken in a screenshot before anyone touches it).

#### C. Wire the completeness assertion into the template's test suite

So a scaffolded app inherits the check **from birth** and cannot drift silently. This is the
highest-leverage single item in the WO.

**A refinement to the ratchet, needed here and worth stating:** the completeness check is a hard failure
only for an app whose adoption WO has landed — a rule that exists so no *existing* consumer goes red
because its maintainer had no capacity yet. A new app has no adoption WO, but it is **adopted by
construction**. The template therefore ships the check as **hard**, and the ratchet's exemption is
understood as protecting the existing estate, not exempting new arrivals.

#### D. The two HTML-level fixes — and they must go together

- Declare `color-scheme: light` so browsers stop painting native controls from a dark palette.
- Add `viewport-fit=cover` to the viewport meta.

**Do not add `viewport-fit=cover` on its own.** It makes the page extend under a notch or rounded
corner, so content is *occluded* unless the layout respects `env(safe-area-inset-*)`. ucm's shared
components carry that padding; the template's own layout may not. **Adding the meta tag without
verifying the template's own layout would turn a latent defect into a live one on notched devices** —
so the meta tag and an inset audit of the template's layout are one item, not two.

#### E. Create the register

`webapp-template` has **no `WORK_ORDERS.md`**. Create it alongside this WO, with a header documenting
the `TPL-*` prefix, following the shape used in `ui-core-micha` and `webapp-management`.

### Non-goals / do not touch

- **The template's tooling drift** — CI, Dockerfile, `run-dev` / `generate-env` conventions, S112,
  register conventions beyond creating the file. That side is actively maintained by another workstream
  (its most recent commit is `feat(ci): split backend Dockerfile … (CI-6)`, 2026-08-01) and the operator
  has assigned the technical debt to a different agent. **Do not open it, and do not create a row for
  it here** — describing or scheduling another agent's workstream is against this estate's convention.
- **The font loading.** Already correct: self-hosted, scoped subsets. Leave it.
- **Dark mode** — DS-12, and the factory ships light tokens only.
- **The mobile shell** — not shared yet (DS-6 waits for its second consumer).
- **Scaffolding a real app to try it out.** Verification runs against the template's own dev server.
- No behaviour, permission or data-contract change beyond what the bump itself brings.

### Risks

- **26 minors in one bump.** Operator-assessed as feature-only apart from a well-tested mail switch
  (2026-08-10). Recorded rather than re-investigated — but if the rendered check shows something
  unexpected, that assessment is the first thing to revisit.
- **`viewport-fit=cover` is a regression risk if shipped alone** — see scope D. This is the item most
  likely to be split off and half-done.
- **The placeholder accent propagates by design.** Every future app inherits it until someone changes
  it, which is both the mechanism and the hazard.
- **Another agent maintains this repo.** Check for in-flight or uncommitted work before touching it —
  a shared working tree means a file read can show another session's intermediate state, and a push can
  carry another session's commit.
- **No register exists**, so there is no highest-ID check to perform — but the prefix check is estate-wide
  and was done: `TPL-*` is unused in all thirteen registers.

### Required tests to WRITE

The template has a `vitest` setup (`frontend/src/App.test.jsx`). Extend it rather than scaffolding a
new harness.

1. The exported theme is built by `createAppTheme`, and `assertThemeComplete` returns **no findings**
   — asserted as a hard failure, per scope C.
2. The placeholder accent is present as a deliberate value and is **not** reported as an
   exemption-less MUI default. Prove non-vacuity by removing `palette.primary` and confirming the
   factory throws.
3. The app still mounts and renders after the bump — extend the existing `App.test.jsx` if it does not
   already assert this.
4. `index.html` carries `viewport-fit=cover` **and** the template's own layout applies
   `env(safe-area-inset-*)` where it reserves edge space. The CSS half is unit-testable; the rendered
   half is below.

Plus whatever lint/typecheck the template already runs.

**No full-suite run** beyond the template's own suite, which is small.

### Verification

- The DS-1 rendered two-width side-by-side (375 px / 1280 px) against the template's own dev server,
  before and after, since there is no prototype artifact for a template.
- **A standard 375 px viewport cannot reveal a safe-area regression** — a desktop browser has no notch.
  So scope D additionally needs a **notched-viewport emulation** (device emulation with safe-area insets,
  e.g. an iPhone profile). Named explicitly because the DS-1 gate as written would pass a broken
  `viewport-fit` change without complaint.
- The completeness assertion green in the template's own suite.

### Preconditions

- `THEME-1` landed and published (`2.30.0`) — the factory and the assertion exist.
- `CHART-6` landed (`2.31.0`). `THEME-2` need not have landed; if it has, pin its patch.

### Parity guardrail

Visual/UX and dependency only. The template's structure, routes, components and backend stay as they
are. A scaffolded app must behave the same as before — it should only look deliberate instead of
default.

---

## B. Implementation map

*To be filled by the Orchestrator on `git pull` — see AGENTS.md → "Work Order".*
