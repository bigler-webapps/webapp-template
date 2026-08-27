# TPL-4 — `.gitattributes` in the template, before the next app needs it

## Part A — Envelope

### Goal

Newly scaffolded applications inherit a `.gitattributes` that pins text files to LF, so a shell
script added later cannot break local development on a Windows checkout.

### Why now

The template ships no shell script today, which is why it has never needed this. But applications
grow them, and two of the four apps taken over in August 2026 demonstrated exactly what happens when
they do:

```
env: 'sh\r': No such file or directory
```

The container restart-loops. The mechanism is not a repository fault — the stored blob is clean LF.
`core.autocrlf = true` on a Windows development machine rewrites LF to CRLF **on checkout**, local
development mounts that working tree into the container, and `env` cannot find an interpreter named
`sh\r`. Diagnosis cost a session; the fix is one file.

Of those four apps, the two that carried a `.gitattributes` were unaffected. That is the whole
evidence base, and it is enough: this is preventive baseline work inherited by newly scaffolded
applications, which is what the `TPL-*` stream is for.

### Scope

One file at the repository root. The set already in service in `Kira`:

```
*.bat text eol=crlf
*.cmd text eol=crlf
*.css text eol=lf
*.html text eol=lf
*.js text eol=lf
*.jsx text eol=lf
*.json text eol=lf
*.md text eol=lf
*.py text eol=lf
*.sh text eol=lf
*.svg text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
```

### Non-goals

- **No retrofit to existing apps.** `WM-TAKE-6` covers the four takeover apps; the six estate apps
  carry no shell scripts and are not affected. Adding it fleet-wide is a separate decision, and this
  WO does not make it.
- No change to `core.autocrlf`. That is a machine setting; pinning it in the repository is precisely
  the point of doing this here instead.

### Tier

**1** — a single attribute file in a repository with no deployment and no database.

### Risks

Adding the file to an existing checkout does not rewrite what is already on disk; it takes effect on
the next checkout or an explicit `git add --renormalize`. For the template that is immaterial — it has
no scripts — but a reader who copies this file into an app and expects an immediate fix will be
puzzled. `WM-TAKE-6` carries that step for the apps that need it.

### Tests

None. There is nothing to run in this repository, and the property being fixed is a property of
checkouts elsewhere. The evidence that it works is `WM-TAKE-6`'s outcome in the four apps.

---

## Part B — Implementation map

### Files

`.gitattributes` at the repository root. Source: `Kira/.gitattributes`, verbatim.

### Reference

`WM-TAKE-6` in `webapp-management` for the failure, the mechanism and the measurement across the four
apps.

---

## Part C — Orchestrator only

*Stop line.*

### Review

Tier 1: read the diff and commit. One file, no logic.

### Register

`TPL-4`. The Notiz names the failure this prevents and points at `WM-TAKE-6`, so the reason survives
longer than the memory of the session that found it.

### Commit

`develop` if it exists in this repository, otherwise `main`, per the infra/template branch rule.
