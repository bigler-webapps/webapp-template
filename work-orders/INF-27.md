# INF-27 — Strip the build toolchain from six backend runtime images (webapp-template)

Cross-repo WO. Canonical Envelope + full rationale: `webapp-management/work-orders/INF-27.md`.
This file is webapp-template's implementation slice of that same WO — same ID, same Envelope, this
repo's map.

---

# A. Envelope — authored by the Expertenchat (copied from the canonical WO, authoritative)

## Goal & expected outcome
- Ziel: `backend/Dockerfile` carries a C toolchain, a set of `-dev` header packages, and the
  WeasyPrint runtime cluster (cairo/pango/gdk-pixbuf) in its **runtime** layer, none of which this
  app needs. Headers/compiler are only needed while `uv pip install` builds wheels (it doesn't need
  to compile anything — every dependency resolves to a wheel); WeasyPrint has no consumer here.
- Expected outcome: `backend/Dockerfile`'s image drops from ~1802 MB to ~688 MB of layers with no
  change in behaviour and no multi-stage split introduced. Measured on spesix (same apt set,
  byte-identical across all six repos in this WO) — see canonical WO for full numbers.

## Scope + non-goals
- In scope: in `backend/Dockerfile`, delete sixteen `apt-get install` lines (compiler + 7 `-dev`
  headers + the 8-package WeasyPrint cluster) and the two-line dead `GDAL_LIBRARY_PATH` block.
  Exact lists in Part B.
- Explicit non-goals / do-not-touch: do NOT remove `libraqm0`, the fonts (`fonts-liberation`,
  `fonts-dejavu`) or `fontconfig` — measured as a bad trade for the last ~25 MB (fonts loss is a
  quiet failure mode; `libraqm0` loss flips Pillow's `raqm` capability off). Do not introduce a
  multi-stage build. No `requirements.txt`, `docker-compose.yml`, CI or database changes.

## Tier · precondition / gate
- Tier: 2 — set by the canonical WO's Envelope, not renegotiated here.
- Precondition: none cross-repo (unlike CI-16, these six pushes are mutually independent — no
  ordering constraint between them). Precondition WITHIN this repo: the `docker build --target
  backend_test` + import smoke test (see Part B) must pass before this repo's diff is handed back
  for review/commit.

## Risks
- A wheel-less dependency in **this repo's own** `requirements.txt` would fail the build — this is
  why the cold-cache build is mandatory per repo rather than inherited from spesix's measurement.
- `libpq-dev` removal is safe only while this repo uses `psycopg2-binary`/`psycopg[binary]` (not a
  bare `psycopg2`) — confirmed in this repo's `requirements.txt` before dispatch, but re-verify.
- A missing runtime library fails at container start, not in a test — loud on staging (healthz),
  not caught by the build/smoke test alone; note this in the register for post-push observation.

## Required tests to WRITE
None. Pure build-input (Dockerfile apt list) change; no application behaviour to assert. The
`docker build` + import smoke test described in Part B is the verification, not a unit test.

---

# B. Implementation map — filled by the Orchestrator — ADDRESSED TO THE IMPLEMENTER

## Context package

- **Named file:** `backend/Dockerfile` — delete these sixteen lines from the `apt-get install`
  list: `build-essential`, `libpq-dev`, `gdal-bin`, `libgdal-dev`, `libproj-dev`, `libgeos-dev`,
  `libffi-dev`, `libcairo2-dev` (compiler + headers); `libcairo2`, `libpango-1.0-0`,
  `libpangocairo-1.0-0`, `libgdk-pixbuf-2.0-0`, `libpangoft2-1.0-0`, `libopenjp2-7`,
  `python3-cffi`, `python3-brotli` (WeasyPrint cluster). Also delete the two-line
  `RUN export GDAL_LIBRARY_PATH=$(find …) && echo "GDAL_LIBRARY_PATH=…" >> /etc/environment` block
  immediately below the apt install (dead: Django reads a setting, never this env var).
- **What must remain, unchanged and in place:** `netcat-openbsd`, `gettext`, `libraqm0`,
  `fonts-liberation`, `fontconfig`, `fonts-dejavu`, `procps`, `curl` — do not reorder, do not
  additionally trim these.
- **Do not touch:** anything else in the Dockerfile (stage boundaries, `COPY` lines, the
  `uv pip install` step, `USER deploy`, `CMD`, the frontend build stage).
- **Mandatory verification (you run this yourself, it is not optional):**
  1. From the repo root: `docker build --no-cache --target backend_test -f backend/Dockerfile -t
     inf27-webapp-template-test .` — confirm exit 0.
  2. Read `backend/requirements.txt` yourself (do not assume another repo's list) and run an import
     smoke test inside the built image, e.g.
     `docker run --rm inf27-webapp-template-test python -c "import django; django.setup(); <imports
     of every native-linked package actually present — psycopg2/psycopg, PIL/Pillow, pillow_heif,
     reportlab, svglib, openpyxl, docxtpl, pypdf, etc>"` — adjust the import list to match what
     this repo's `requirements.txt` actually declares.
  3. Report the exact commands and their exit codes/output in `PROGRESS`/`RESULT`.
- Directive: work from this package only; open `backend/Dockerfile` and `backend/requirements.txt`
  to verify, make the deletions, run the build + smoke test, stop.

## Target repo working directory (absolute)

`C:\Users\Micha Bigler\Documents\webapps\webapp-template`

## Preamble

> The text above is the COMPLETE spec — the committed WO file's content, not a plan to refine; there
> is no separate plan file. Read the nearest `AGENTS.md`, the relevant `.codex/skills/<role>/SKILL.md`, and the
> app `MEMORY.md` ONLY for conventions. Stay in scope; do not touch auth/permissions/deps/schema/CI
> beyond the named Dockerfile lines; do not update `MEMORY.md`. **Do NOT edit `WORK_ORDERS.md` — the
> register row and the review verdicts are the orchestrator's alone.** Do NOT `git add`/`commit`/`push`
> — leave the change uncommitted in the working tree for the orchestrator's independent review. No
> unit tests are required (see Part A) — but the `docker build` + import smoke test above IS
> required and is the one verification action you perform yourself; do NOT run the app's
> affected/full pytest/vitest suite, and do NOT run any review.
>
> Narrate continuously: a `PLAN: <step1> | <step2> | …` line up front, then a single-line
> `PROGRESS: [<n>/<total>] <present-tense action>` before every relevant action (and `… done` on
> completion), spaced so no gap exceeds ~2 min, stdout unbuffered, plus exactly one final
> `RESULT: DONE|BLOCKED <reason>` that states the build/smoke-test outcome explicitly.

---

# C. Orchestrator only — NOT ADDRESSED TO THE IMPLEMENTER

> **If you are the implementer reading this work order as your own specification: STOP at this line.
> Everything below describes what the Orchestrator does AFTER you finish. You do none of it — no
> reviewers, no verification run, no register edit, no commit.** You ARE the invocation described
> below; do NOT shell out to `codex exec`.

## Execution directive

Implement through `codex exec` in the background — invoked directly via Bash (never the
`debugger`/`*_coder` Agent wrappers) with BOTH flags `--skip-git-repo-check` and
`--dangerously-bypass-approvals-and-sandbox`. Fallback to direct Claude implementation only on
Codex quota/rate-limit/non-zero exit — flips authorship, independent reviewer becomes mandatory.
Independent of the other five repos in this WO — no ordering constraint, may run concurrently.

## Review routing

Tier 2, no new logic (pure deletion): `reviewer` is not tier-mandatory, but the Orchestrator spawns
one anyway (Haiku) given the real behavioural risk class (wheel-less dependency / missing runtime
lib) despite the low tier floor — proportionate to six independent blast radii. No `ui_reviewer`
(not frontend). No `sec_reviewer` (not auth/security).

## Verification

Confirm the diff touches only the sixteen apt lines + the two-line GDAL block, nothing else.
Confirm the reported `docker build --target backend_test` exit code and import smoke test output.
No pytest/vitest run. Note in the register that staging healthz should be watched after the push
(the push itself triggers the deploy that is the real runtime-library check).

## Register + commit

Add an `INF-27` row to this repo's `WORK_ORDERS.md` (Tier 2, cross-ref
`webapp-management/work-orders/INF-27.md`), named review verdict + build/smoke-test outcome, then
commit + push to `main` — independent of the other five repos in this WO.
