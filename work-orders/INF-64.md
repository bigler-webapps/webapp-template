# INF-64 — ucm catch-up: `2.41.3` → `3.2.0`

## Part A — Envelope

**Goal.** Bring `@micha.bigler/ui-core-micha` in `frontend/package.json` up to the latest
published version (`3.2.0`); `django-core-micha` is already pinned to the latest published
release (`2.43.0`), so this WO is ucm-only.

**Why now.** The template scaffolds every new app; leaving it two majors behind means each new
app inherits a stale pin from day one.

**Scope.** `frontend/package.json` (the version specifier) + `frontend/pnpm-lock.yaml`
(regenerated via `pnpm install`). No application source file changes.

**Non-goals / do-not-touch.** No chart-related code — this app has none. No `createAppTheme`
changes (already adopted, `TPL-1`). No unrelated dependency bumps.

**Tier.** 2. Classification per `AGENTS.md` → Tiering's dependency-bump test ("purely
additive... is Tier 2... read the changelog or version diff, never assume additive"):
`ui-core-micha`'s `CHANGELOG.md` shows every entry from `3.0.0` through `3.2.0` is chart-scoped
(`UCM-CHART-12`–`15`: `ChartFrame`/`resolveChartLayout`/chart size presets — two of them
explicitly breaking for chart consumers). A commit-level check (`git log 11d362c..be2eb6b --
src/`, the 2.41.3→3.2.0 boundary commits in `ui-core-micha`) confirms all 8 commits touching
`src/` in that range are chart-only. webapp-template's `frontend/src` has zero chart usage
(grepped: no `Chart`/`chart` match anywhere) and its full ui-core-micha import list —
`AuthProvider`, `LoginPage`, `PasswordInvitePage`, `PasswordResetRequestPage`, `SignUpPage`,
`SignupConfirmPage`, `AuthContext`, `updateUserProfile`, `ProfileComponent`, `WidePage`,
`AccountPage`, `createAppTheme`, `assertThemeComplete` — is named nowhere in those changelog
entries. Additive for this consumer; no new logic is introduced by the bump itself.

**Risks.** None identified against this app's actual usage surface; the chart-subsystem breaking
changes are out of this app's blast radius. Residual, not blocking: `ui-core-micha`'s changelog
only logs "notable, user-facing changes" (not every version) — covered here by cross-checking the
full commit log for the range, not the changelog alone.

**Tests.** Existing frontend suite (`pnpm test`, 2 files / 6 tests) + `pnpm build` (production
build) as a smoke check. No new tests — the bump changes no behavior this app exercises.

## Part B — Implementation map

Implemented directly by the Orchestrator (`.claude/models.local.json` default:
`implementation.runtime: claude`) — no Codex dispatch, single mechanical edit:

- `frontend/package.json:9` — bump the `@micha.bigler/ui-core-micha` specifier `2.41.3` → `3.2.0`.
- `frontend/pnpm-lock.yaml` — regenerate via `pnpm install` in `frontend/`.

## Part C — Orchestrator only

- Reviewer routing (Tier 2, frontend diff, no new logic): `ui_reviewer` only, per
  `.claude/models.local.json` default (`ui_review: claude/sonnet`). No general `reviewer` (no new
  logic).
- Verification: `pnpm test` and `pnpm build` in `frontend/`, both must exit 0.
- Register: add row `INF-64` to `WORK_ORDERS.md`, status `done`, with the review disposition
  recorded in Notiz.
- Commit: single commit on `main` (this repo has no `develop`) once review + tests are green.
