# WT-SYNC-1 — Close out the two pending back-port PRs

Prepared: 2026-10-15. Target repository: `webapp-template` (`main`).

# A. Envelope — addressed to everyone

## Goal and expected outcome

webapp-template has no open PR left. Each of the two back-port PRs from hram is either merged (still applicable and generic) or closed with the reason.

## Tier

Tier 2: template content, no deploy.

## Operator decisions this Envelope records (2026-10-15)

1. #19 (week of 2026-06-18: `.github/workflows/main.yml`, `backend/requirements.txt`; conflicting today) and #23 (week of 2026-10-08: `.gitignore`, `backend/.coveragerc`, `backend/requirements.txt`, `backend/utils/tests.py`, `backend/utils/views.py`, `frontend/vite.config.mts`) are reviewed one by one against today's template and today's hram.
2. A change that is still generic and not yet in the template is merged (#19 rebased to resolve its conflict); a change that is superseded, hram-specific or already present is closed with a one-line reason. Parts of a PR may be taken and the rest dropped; the PR is then closed with a pointer to the commit that took the useful part.

## Scope

1. Decisions 1 and 2. The template's own CI green on the result.

## Non-goals

- Bringing the template up to date beyond these two PRs (`maana/TPL-5`).

## Risks

- A wrong merge shows only when a new app is created from the template. Mitigation: the template's CI and the one-by-one review.

## Required tests to write

None; the template's own CI is the check. `backend/utils/tests.py` from #23 comes with its own tests if it is merged.

# B. Implementation map — addressed to the implementer

*To be filled by the Orchestrator.*

# C. Orchestrator only — not addressed to the implementer

> **If this WO was dispatched to you as an implementer: STOP here.**

Gate #1 open until recorded in the register row. Part of the PR close-out round of 2026-10-15.
