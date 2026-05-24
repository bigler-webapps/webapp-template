# APP_FINDINGS.md — &lt;tenant-name&gt;

This file is the **per-tenant security-findings tracker**. The central
`webapp-management/SECURITY_FINDINGS.md` carries cross-tenant findings
(S1–S181+); this file carries only **app-specific** findings discovered
during reviews of the consuming repo.

After "Use this template", replace `<tenant-name>` with your app name and
delete this introductory note.

## How to use

When a reviewer (human or sec_reviewer agent) finds an issue:

1. Pick the next un-used finding-ID. App-specific IDs use the format
   `<APP>-NEW-<short-name>` where `<APP>` is your tenant's short tag
   (e.g. `HRAM`, `JG`, `KZ`).
2. Add an entry under the appropriate severity section (P1 / P2 / P3)
   using the template below.
3. When the finding is fixed, mark it `_Closed in <branch-name>._` and
   keep the entry in place for the audit trail.
4. After a deep-audit pass, when this file accumulates ≥3 closed
   findings, request an S-number range from the platform maintainer to
   assign canonical S-IDs (mirror pattern: every per-tenant
   `<APP>-NEW-<name>` gets a stable `S<NNN>` prefix).

## What you do NOT add here

- Platform-wide findings (auth-lib, infra, Traefik middlewares) — those
  go to `webapp-management/SECURITY_FINDINGS.md`.
- Tenant-onboarding TODOs — those go to your repo's `TODO.md` or
  `docs/onboarding.md`.

---

## P1 — Immediate exposure

_(no current findings)_

---

## P2 — Major

_(no current findings)_

---

## P3 — Tracking

_(no current findings)_

---

## Residual risks / lower-confidence

_(none documented)_

---

## Finding template

```markdown
### <APP>-NEW-<short-name> — <one-line title>
**Severity:** P2
**File:** `<repo-relative-path>:<line>`
**Confidence:** high / medium / low
**Issue:** <one paragraph describing the bug>
**Repro:** <specific steps>
**Fix:** <specific recommendation>
```

After fixing, append `_Closed in <branch-name>._` at the end of the
`**Fix:**` block (do not delete the entry — keep the audit trail).
