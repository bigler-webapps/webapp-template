@AGENTS.md

## Agent-Guardrails

> Gilt für alle Sessions und besonders für autonome Routines (die kein
> Approval-Gate im Loop haben).

- **Working tree:** Vor Code-Änderungen `git status`. Ist der Tree nicht clean
  oder erscheinen unerwartete Dateien im Diff → **stoppen und den Operator fragen**.
  Fremde/unerwartete Änderungen NIEMALS reverten oder verwerfen.
- **Standard-Entwicklungsbranch: `develop`.** Direkt auf den Trunk committen —
  KEINE Feature-Branches (harness-blockiert). Einziger PR ist `develop → main`
  (Promotion zum geschützten `main`). Siehe root `AGENTS.md` → "Branch discipline".
- **Branch-Wechsel nur nach expliziter Bestätigung** (`git checkout <branch>` /
  `git switch`).
- `git checkout/restore/reset --hard/clean`, force-push, `gh secret set`,
  `gh auth token` und direkte `proton-pass-cli`-Aufrufe sind in
  `.claude/settings.json` gesperrt (hartes Enforcement).
