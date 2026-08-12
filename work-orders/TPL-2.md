# TPL-2 — Stop shipping an unenforced frontend suite to every new app

**Target repo:** `webapp-template` (branch `main` — check for `develop` first)
**Tier:** 3 — touches CI.
**Review:** independent `reviewer` — mandatory. `ui_reviewer` does not apply: a workflow input and a
comment, no rendered output.
**Unblocked 2026-08-12** — `cockpit/UI-12` landed and its CI run is green: **12 files / 92 tests in
47.68 s** ([run 31590500379](https://github.com/bigler-webapps/cockpit/actions/runs/31590500379)), with
both `UI-10`'s and `UI-11`'s hard assertions among the files that ran.

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

### What cockpit's run settled, including one correction to this WO's own claim

`cockpit/UI-12` flipped the same input in one real app first, deliberately, because the template's blast
radius is every future scaffold. The result:

- **The shared workflow runs vitest fine.** 12 files, 92 tests, **47.68 s**. So the inherited
  "adds ~30 s per run" comment was in the right ballpark after all — an earlier draft of this WO called
  it wrong by an order of magnitude, which came from broken local runs and is retracted.
- **The flag does not give per-push enforcement, and this WO must not claim it does.** `ci.yml` triggers
  only on `pull_request` and `workflow_dispatch` — never on a plain push. Since these apps commit
  straight to the trunk and the only PR is the `develop → main` promotion, flipping the flag means the
  frontend suite runs **on the promotion PR and on manual dispatch**. cockpit's green run needed a
  dispatch to happen at all.

That is weaker than "blocks a commit", and it is also exactly what `AGENTS.md` designs for: the narrow
per-change set is the local gate, and **the full suite is the promotion gate's job.** So the value here is
real but specific — a new app's promotion PR will exercise its frontend suite instead of silently never
running it.

**Worth knowing rather than fixing here:** if per-push enforcement is actually wanted, that is a
`ci.yml` trigger change across the estate, a separate decision, and not something to smuggle into a
template default.

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
