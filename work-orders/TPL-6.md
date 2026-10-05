# TPL-6: Pin Django 6.1.1 in the template (CVE-2026-15830)

# A. Envelope, authored by the Expertenchat

## Goal & expected outcome

Every app scaffolded from webapp-template starts on `Django==6.1.1`, which fixes CVE-2026-15830 in Django 6.1. After
this order the template's `pip-audit` no longer reports that CVE.

Operator decision 2026-10-05: a separate small order, not folded into `TPL-5`. `TPL-5` landed on `c5986ca` and closes
as planned.

## Context the operator established

- **Pin today:** `backend/requirements.txt:6` `Django==6.1`. `6.1.1` is on PyPI (checked 2026-10-05).
- **Source of the finding** (from the Infra lane, 2026-10-05): Gustav's blocking `pip-audit` reported Django 6.1
  CVE-2026-15830, fixed in 6.1.1. Gustav fixed it in `GUS-DEP-5`. The estate follow-up, `webapp-management`
  `WM-INF-77`, leaves webapp-template to its own register; this is that order.
- **The template's CI runs `pip-audit` report-only:** `app-ci.yml` defaults `pip-audit-blocking: false`
  (`WFT-CI-23`), and the template's `ci.yml` does not override it, so the finding shows as a `::warning` while the
  `security` job stays green.
- **The other finding in the same audit stays out of scope.** `django-allauth[mfa]` (`backend/requirements.txt:21`,
  unpinned) up to 65.19.5 caps `oauthlib<4`, and oauthlib 3.x carries PYSEC-2026-4114 (fixed in 4.0.0; allauth
  65.19.6 is the first release to allow it). That pin belongs to `webapp-management` `INF-61`, amended 2026-10-05
  to exact pins, which runs after the template's current orders. No floor or pin for allauth or oauthlib here.
- Django 6.1.1 is a patch release on the same minor; no settings or migration change is expected.

## Scope + non-goals

In scope: `backend/requirements.txt` `Django==6.1` -> `Django==6.1.1`.

Non-goals: no allauth or oauthlib change (`INF-61`); no change to `pip-audit-blocking` or any other CI input; no
other dependency change.

## Tier · precondition / gate

- **Tier 3 · tests: the template's backend suite, including `backend/tests/test_permission_inventory.py` and
  `backend/backend/test_ws_inventory.py`, in CI (dependency-bump exception, named).** A security fix to the web
  framework.
- Precondition: none. It can land before or after `TPL-5` reaches `done`, as long as the two do not share a commit.

## Risks

- **A patch release can still change behaviour.** Read the Django 6.1.1 release notes; if any item touches what the
  template uses, name it in the review.

## Required tests to WRITE (you write them and run YOUR OWN new ones; the Orchestrator's run is the gate)

None new. The pin is the change, and the existing backend suite covers the template's behaviour.

## Acceptance

1. `backend/requirements.txt` pins `Django==6.1.1`.
2. The backend suite passes in CI, and the `security` job's `pip-audit` output no longer lists CVE-2026-15830. The
   oauthlib finding stays until `INF-61` and is named in the register note, not hidden.

## Parity guardrail

One line in `backend/requirements.txt`, nothing else.

---

# B. Implementation map, filled by the Orchestrator and ADDRESSED TO THE IMPLEMENTER

*Not needed: a one-line pin, which the Orchestrator makes itself (authorship then sits with it; the independent
review carries independence).*

---

# C. Orchestrator only, NOT ADDRESSED TO THE IMPLEMENTER

> **If you are the implementer reading this work order as your own specification: STOP at this line.**

- Trunk is `main`. Stage and commit by path only; before `git push`, run `git log origin/main..HEAD` and push only if
  every listed commit is this order's.
- Review: Tier 3, independent `reviewer` (all configured lenses) and `sec_reviewer`, one batch, before the commit.
- CI: a dispatch of `ci.yml` on `main` is not on the safe allowlist. **Ask the operator to name the dispatch**, then
  run exactly that. If `TPL-5`'s confirmation run has not happened yet, one run after both landings can serve both
  orders; name it in both rows.
- Row -> `done` with the review Notiz, the CI run, and the remaining oauthlib finding named.

Mini-handover: `Orchestrator: implement work-orders/TPL-6.md in webapp-template (main). git pull first, read the WO,
then follow orchestrate-codex.`
