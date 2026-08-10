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

*Filled by the Orchestrator on `git pull` — see AGENTS.md → "Work Order".*

### Execution directive (read this first)

> **If you are the implementer reading this work order as your own specification: this section is
> NOT addressed to you.** It tells the Orchestrator how to invoke you. **You ARE that invocation —
> do NOT shell out to `codex exec`.**
>
> Implement through `codex exec` in the background — invoked directly via Bash (never the
> `debugger`/`*_coder` Agent wrappers) with BOTH flags `--skip-git-repo-check` and
> `--dangerously-bypass-approvals-and-sandbox`. **Pass the WO via stdin, not as a positional
> argument** — `cat work-orders/TPL-1.md | codex exec --skip-git-repo-check
> --dangerously-bypass-approvals-and-sandbox -` (a positional arg hits Windows' command-line length
> limit on a WO this size — proven repeatedly in `ui-core-micha`). Fallback to direct Claude
> implementation only on Codex quota/rate-limit/non-zero exit.

### Context package

**Preconditions verified 2026-08-10:** THEME-1 (`2.30.0`) and CHART-6 (`2.31.0`) are landed and
published; the currently published version is **`2.31.1`** (THEME-2 has landed too — per the WO,
"if it has, pin its patch"). **Pin exactly `2.31.1`**, not `2.31.0` — confirm this is still current
via `npm view @micha.bigler/ui-core-micha version` at implementation time in case another patch
landed between mapping and execution.

**Repo state verified 2026-08-10:** working tree clean on `main`, no uncommitted foreign work found
(the WO's Risk section warns another agent maintains this repo — re-run `git status` yourself before
editing, per the standard orientation step, in case that has changed since this map was written).

**Named files and their exact current content (read in full during mapping — the whole files are
short, reproduced/pointed at below so you don't need to re-discover them):**

- `frontend/src/theme.js` (98 lines) — hand-rolled `createTheme` with: a custom `breakpoints` set
  (adds an `xxl: 1680` step — **verified unused anywhere else in `frontend/src`**, grep confirms no
  `xxl`/`breakpoints.up('xxl')` reference in any component, safe to drop), `palette.primary.main:
  '#468AB2'`, `palette.secondary.main: '#BF3227'` (**also verified unused elsewhere** — no
  `color="secondary"`/`palette.secondary` reference in the app's own components), `palette.background
  .default: '#FFFFFF'` (baseline's own default is `#FAFAFA` — dropping this is intentional, matches
  scope B), `typography.fontFamily` + per-variant `fontWeight`/`letterSpacing` overrides that
  duplicate/conflict with the baseline's own type scale, and `components.MuiButton`/`MuiTableCell`
  style overrides that duplicate what THEME-1's baseline already provides (radius, padding,
  textTransform, table-cell padding). **Replace the whole file with `createAppTheme({ palette: {
  primary: { main: '<placeholder>' } }, typography: { fontFamily: "'DM Sans', sans-serif" } })`** —
  exactly the two things scope B calls "the palette and the font, nothing else". Keep the
  `@fontsource/dm-sans` CSS imports at the top only if `createAppTheme` doesn't already load them
  itself (THEME-1's `createAppTheme` imports `@fontsource/dm-sans/400.css` etc. as a side effect —
  check whether the template's `latin-400.css` subset variant is still needed alongside/instead of
  the factory's own import, since the template deliberately uses SCOPED LATIN SUBSETS
  (`@fontsource/dm-sans/latin-400.css` etc., smaller payload) while the factory imports the
  unscoped `/400.css` — the WO's own evidence table says font loading is "already correct... leave it
  alone", so keep the template's scoped-subset imports in `theme.js` even though this means BOTH the
  factory's own unscoped import AND the template's scoped one may load — note this explicitly rather
  than silently dropping either, and if double-loading is wasteful, say so as a finding rather than
  guessing at a fix outside this WO's font-loading non-goal).
- **The placeholder accent (scope B's "one real decision").** Use a visibly provisional value, e.g.
  `#FF00FF`, with an adjacent `// TODO: replace with this app's accent` comment — per the WO's own
  recommendation. This is explicitly a taste call the operator may overrule at Gate #1; implement the
  recommendation as given, don't invent a different placeholder scheme.
- `frontend/index.html` (13 lines) — `<meta name="viewport" content="width=device-width,
  initial-scale=1" />` at line 5. Change to `content="width=device-width, initial-scale=1,
  viewport-fit=cover"`. No `color-scheme` anywhere in `index.html`/`App.css`/`index.css`.
- `frontend/src/index.css` — add `color-scheme: light` (to `:root` or `body`, your call, but it must
  apply globally — `body { margin: 0; font-family: ...; color-scheme: light; ... }` is the simplest
  correct placement, matching where the file already sets global body-level rules).
- **Safe-area audit (scope D — do not skip, do not treat as a separate follow-up):**
  `frontend/src/App.css`'s `.App`/`.App-header`/`.App-logo`/`.App-link` classes are **dead CRA
  boilerplate — verified unused anywhere in JSX** (`grep -rn "App-header\|App-logo\|className=\"App\""
  frontend/src --include=*.jsx` returns nothing). There is therefore no full-bleed hero layout to
  patch. The real layout is `frontend/src/components/Header.jsx`'s MUI `<AppBar position="static">`
  at the top of the document (rendered before `<Routes>` in `App.jsx`) — with `viewport-fit=cover`,
  the page canvas extends under a device notch/rounded corners/home-indicator, so content pinned at
  the true top/bottom/side edges of the viewport (which the `AppBar`, sitting at document-flow top,
  effectively is) can be visually clipped by a notch in portrait or by the curved screen edge in
  landscape. Add `env(safe-area-inset-*)` padding at the OUTERMOST level so it applies once, not
  per-component — the simplest correct placement is `body`'s existing rule block in `index.css`:
  `padding-left: env(safe-area-inset-left); padding-right: env(safe-area-inset-right);` (top/bottom
  insets are usually left to individual fixed-position elements, but since this app has none besides
  the static top AppBar, adding `padding-top: env(safe-area-inset-top)` there too is the safer,
  simpler choice for a template baseline — state which you chose and why). These resolve to `0` on
  non-notched devices/browsers with no `viewport-fit=cover` set, so this is safe to ship unconditionally
  — confirm that is genuinely how `env()` behaves here (it is, per the CSS Env spec — `env()` with no
  matching value defaults to `0` unless a fallback is given) rather than assuming.
  **Also verify `.App`/dead CRA CSS is not accidentally load-bearing elsewhere** (e.g. `App.jsx`
  itself doesn't import `App.css` for a class it does use) before touching it — read `App.jsx`'s own
  imports to confirm `./App.css` is only ever imported for those four unused classes.
- **The "mail switch" glance (scope A):** verified 2026-08-10 — the template's `frontend/src` does
  **not** import or wire `OnboardingProvider`, `NotificationsProvider`, `browserPush`, or any
  onboarding/notification component from `ui-core-micha` at all (`grep -rln
  "Onboarding\|Notifications\|browserPush" frontend/src` returns nothing). The candidate ucm commits
  in the 2.5.0→2.31.1 range that touch email/notification defaults
  (`refactor(notifications): make push settings a toggle to match email`,
  `feat(onboarding): combine email opt-in and browser push notifications`) therefore have **no
  surface in this template to carry an inherited default** — state this explicitly as the WO's "one
  glance" outcome rather than digging further; there is nothing to configure.
- `frontend/src/App.test.jsx` (11 lines) — currently a bare jsdom sanity check with no real render.
  Extend it (don't create a second test file) with the 4 required tests below. You will need to
  actually render `<App />` (or a narrower slice — your call whether a full router render or a direct
  `theme.js` import + `assertThemeComplete` call is the right unit for each of the 4 tests; they don't
  all need a full app render).
- **`WORK_ORDERS.md` — does not exist, create it** at repo root, following the shape of
  `ui-core-micha/WORK_ORDERS.md` and `webapp-management/WORK_ORDERS.md` (both read in full during a
  prior session, structure: intro paragraph, "## Workstream prefixes" table, "## Register" one
  Markdown table). Header documents the new `TPL-*` prefix (confirmed unused estate-wide by the
  Expertenchat). Add the TPL-1 row at finalize time, same as every other repo's register.

### Named files to change / create

- `frontend/src/theme.js` — replaced with the `createAppTheme` call (palette + font only).
- `frontend/index.html` — `viewport-fit=cover` added to the viewport meta.
- `frontend/src/index.css` — `color-scheme: light` + `env(safe-area-inset-*)` padding added.
- `frontend/src/App.css` — the dead `.App`/`.App-header`/`.App-logo`/`.App-link` rules: leave them
  (removing dead CSS is not this WO's scope and risks looking like unrelated cleanup) UNLESS your
  audit finds they actually need the safe-area treatment too (they don't, per the above) — state
  explicitly that they were left alone and why.
- `frontend/package.json` — `"@micha.bigler/ui-core-micha"` pin bumped from `2.5.0` to the current
  published version (`2.31.1` at mapping time — re-verify).
- `frontend/src/App.test.jsx` — extended with the 4 required tests.
- `WORK_ORDERS.md` (new, repo root).

### Do-not-touch / invariants

- **CI, Dockerfile, `run-dev`/`generate-env` conventions, S112, register conventions beyond creating
  the file** — actively owned by a different workstream (most recent: `feat(ci): split backend
  Dockerfile … (CI-6)`, 2026-08-01). Do not open these, do not describe or schedule that workstream's
  work in the new `WORK_ORDERS.md`.
- **Font loading** — already correct (self-hosted, scoped subsets); the only touch is theme.js
  keeping its own scoped imports as noted above, nothing in the font pipeline itself changes.
- **Dark mode, the mobile shell** — out of scope (DS-12, DS-6).
- **No app is scaffolded to try this out** — verification is against the template's own dev server
  directly.
- **The backend, routes, components, `App.jsx`'s structure** — untouched beyond what the bump/theme
  swap requires. `Header.jsx`'s actual JSX is untouched (only global CSS gains safe-area padding).

### Pitfalls (verified against landed code 2026-08-10)

- `xxl` breakpoint and `secondary` palette colour are unused in this repo's own components — confirmed
  by grep, safe to drop as part of "palette and font, nothing else." If a future grep during
  implementation finds a use you missed, keep it and say so rather than silently breaking a real
  reference.
- `.App-header` etc. in `App.css` are dead CRA boilerplate, not a real full-bleed layout — don't spend
  effort "fixing" them for safe-area; the AppBar is the real top-of-document element that matters.
- The scoped-vs-unscoped `@fontsource/dm-sans` import overlap (template's `latin-400.css` vs. the
  factory's own `/400.css` side-effect import) is a real, if minor, double-load — surface it as a
  finding, don't silently resolve it outside the WO's stated font-loading non-goal.

### Target repo working directory (absolute)

`C:\Users\biglmi\Documents\webapps\webapp-template`

### Required tests to WRITE (Codex writes them; the Orchestrator runs them)

Exactly the 4 tests enumerated in Envelope § "Required tests to WRITE" above, extending
`frontend/src/App.test.jsx`. Plus whatever lint/typecheck the template already runs (`pnpm lint` —
this repo has no separate `tsc`/build-check script beyond ESLint, confirm via `package.json`'s
`scripts` before assuming one exists). No full-suite run beyond this template's own (small) suite.

### Verification

- The Orchestrator runs the **DS-1 two-width rendered side-by-side** (375px/1280px) against the
  template's own dev server, before and after — no prototype artifact exists for a template, so this
  compares the running app to itself pre/post change (theme visibly shifts to the placeholder accent
  and baseline type scale; layout/structure must otherwise be identical).
- **A notched-viewport emulation is additionally required** (e.g. resize/emulate an iPhone profile
  with safe-area insets) — a standard desktop 375px viewport cannot reveal a safe-area regression, and
  this is explicitly named in the WO as the check the DS-1 gate alone would miss.
- The completeness assertion green (hard-asserted) in the template's own suite.

### Preamble (append verbatim)

> The text above is the COMPLETE spec — the committed WO file's content, not a plan to refine; there
> is no separate plan file. Read the nearest `AGENTS.md`, the relevant `.codex/skills/<role>/SKILL.md`, and the
> app `MEMORY.md` ONLY for conventions. Stay in scope; do not touch auth/permissions/CI/Dockerfile
> unless the spec says so (the dependency bump itself IS in scope — see Scope A); do not update
> `MEMORY.md`. Do NOT `git add`/`commit`/`push` — leave every change uncommitted in the working tree
> for the orchestrator's independent review. WRITE the tests the `Required tests` section calls for
> AND **RUN the tests you just wrote** to confirm they execute and pass — that is the ONLY test run
> you do (NOT the app's affected/full suite, NOT any review). The orchestrator re-runs the
> authoritative set + does the independent review after you finish — those are the gate; your own run
> does not count as the gate.
>
> Narrate continuously: a `PLAN: <step1> | <step2> | …` line up front, then a single-line
> `PROGRESS: [<n>/<total>] <present-tense action>` before every relevant action (and `… done` on
> completion), spaced so no gap exceeds ~2 min, stdout unbuffered, plus exactly one final
> `RESULT: DONE|BLOCKED <reason>`.

### Mini-handover

Repo: `webapp-template` (`C:\Users\biglmi\Documents\webapps\webapp-template`), branch `main` (only
branch). WO: `work-orders/TPL-1.md`. Follow `orchestrate-codex`.
