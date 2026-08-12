# TPL-2 — Stop shipping an unenforced frontend suite to every new app

**Target repo:** `webapp-template` (branch `main` — check for `develop` first)
**Tier:** 3 — touches CI.
**Review:** independent `reviewer` — mandatory. `ui_reviewer` does not apply: a workflow input and a
comment, no rendered output.
**Blocked on:** `cockpit/UI-12`'s **CI run**. See "Why this waits".

---

## A. Envelope

### Goal

`.github/workflows/ci.yml` ships `run-frontend-tests: false`. Every app scaffolded from this template
inherits it, and the flag then never gets revisited — measured across the estate on 2026-08-12: `true`
in hram, jg-ferien, survey_app, reimbursements, innoservice (five apps that each opted in by hand),
`false` in cockpit, spesix, fitness-monitor **and here**.

This is the same propagation mechanism as the `#468AB2` accent that `TPL-1` fixed: **whatever the
template ships becomes the default wherever nobody looked.** The consequence is concrete — `FM-12`'s
`assertThemeComplete` and `FM-14`'s raw-key assertion sit unenforced in fitness-monitor, and `UI-10`'s
and `UI-11`'s in cockpit, because all four landed in apps whose CI never runs vitest.

Ship `true`, so a new app has to opt *out* deliberately rather than inherit silence.

### Why this waits on cockpit

Flipping the template's default is the one change that stops the bleeding, and it is also the one with
the widest blast radius: **every future scaffold**. If the shared workflow cannot actually run vitest,
this change makes every new app red on day one.

`cockpit/UI-12` flips the same input in one real app. **Let its CI run answer the question first** — one
app learning it beats four. If cockpit's frontend job goes green, this becomes a two-line change with
evidence behind it. If it fails, we have learned that on an existing app rather than on every future one.

### The local measurements are not evidence — mine contradict each other

Three runs on 2026-08-12, same machine:

- cockpit's full suite: **2 of 11 files, nine "Worker exited unexpectedly", 465 s** — but two other
  sessions were building concurrently.
- cockpit's `Header.test.jsx` alone: **8 tests green in 105 s**, then a warm re-run of the same file
  **errored with all sub-timings at 0 ms**.
- **this template's single test file, on an idle machine (zero node processes): "no tests", one error,
  `[vitest-pool]: Worker forks emitted error` → "Worker exited unexpectedly".**

Meanwhile `UI-11`'s landing reported cockpit at **92/92 green**.

So the same suites pass and crash on the same machine, and a single test file dies on an idle one. The
failure is intermittent and environmental — plausibly the vitest-4-forks / jsdom-29 / Node-24 / Windows
combination — and **not something these numbers can pin down.** Treat none of them as a basis for a code
change here.

**In particular: do not "fix" this template's test setup on the strength of the crash above.** If the
template's one test file genuinely cannot run, that is its own work order with its own diagnosis, made on
an environment that measures reliably. CI is that environment.

### Scope

1. `.github/workflows/ci.yml` — `run-frontend-tests: false` → `true`.
2. Replace the inherited comment. It reads "opt-in — adds ~30 s per run"; that number has never been
   checked against a real app and three apps opted out with it as the stated reason. Put the runtime from
   **cockpit's** green CI run there, and say which app it came from.
3. Nothing else.

### Non-goals / do not touch

- **The template's test setup, `vite.config`, or its one test file.** See above.
- **`spesix` and `fitness-monitor`** — one work order each, in their own repos, each gated the same way.
- `run-backend`, `backend-target`, every other input, and every other workflow.
- Any application code, theme value or dependency.

### Risks

- **Widest blast radius in the estate**: every future scaffold. Hence the gate on cockpit's CI run.
- A template change is invisible until someone scaffolds. If the flip turns out wrong, the app that
  discovers it will be a brand-new one whose owner has no context — which is exactly why the evidence
  has to come first.

### Required tests to WRITE

None. The change is a workflow input.

**Acceptance:** cockpit's `UI-12` CI run is green **before** this lands, and this WO's note records that
run's identifier and runtime.

### Verification

There is nothing to render and nothing to run locally that would mean anything — see the measurement
section. The verification is the cockpit evidence plus, ideally, one scaffold-and-push after this lands,
which is worth doing once rather than assuming.

### Parity guardrail

No behaviour change in the template or in any app. What changes is what a new app inherits.

---

## B. Implementation map

*Filled by the Orchestrator on `git pull` — see `AGENTS.md` → "Work Order".*

### Execution directive (read this first)

> **If you are the implementer reading this work order as your own specification: this section is NOT
> addressed to you.** It tells the Orchestrator how to invoke you. **You ARE that invocation — do NOT
> shell out to `codex exec`.**
>
> **Check `.claude/codex-status.md` first** — `unavailable` is recorded for 2026-08-12; on that date
> implement directly in Claude and name the record, which flips authorship and keeps the independent
> `reviewer` mandatory. On a later date with no line, one Codex attempt, outcome written back either way.
>
> **Do NOT edit `WORK_ORDERS.md`**; read `git log origin/<trunk>..HEAD` and `git status` first.
> **Confirm the trunk**: this repo may have `develop`; if it does, that is the target, not `main`.

### Mini-handover

Repo: `webapp-template`. WO: `work-orders/TPL-2.md`. **Blocked until `cockpit/UI-12`'s CI run is green** —
then it is two lines. Follow `orchestrate-codex`.
