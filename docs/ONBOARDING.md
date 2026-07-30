# Neue App onboarden — Checkliste

> Kopiervorlage für `webapp-template` → App-Repo.
> Schritte in Reihenfolge abarbeiten. Constraints am Ende bei jedem Abschnitt mitdenken — sie entstanden aus echten Fehlern.

---

## Phase 0 — Orientieren + Ist/Soll erfassen

- App-`CLAUDE.md` Pflichtlektüre lesen (falls vorhanden, z. B. `docs/architecture.md`).
- Diff erfassen: was hat die App vs. was verlangt das Template  
  (Workflows, `project.yaml`-Shape, Settings, Pins, `urls.py`, WS, Tests)?
- Latest-Versionen ermitteln (nicht raten):  
  aktueller `deploy-app@vX.Y.Z`-Tag (workflow-templates), `django-core-micha==`, `@micha.bigler/ui-core-micha==` (vgl. hram als Referenz).
- Dieses Template bringt `.pre-commit-config.yaml` fuer Secret-Scanning mit gitleaks und detect-secrets mit. In einem frischen Clone einmal `pre-commit install` ausfuehren, damit die Hooks lokal vor jedem Commit laufen.
- `cd webapp-template && git pull` — sicherstellen, dass die eigene Template-Kopie aktuell ist.

---

## Phase 1 — Deploy funktioniert (Plattform-Schicht)

### `.github/workflows/`
- `ci.yml` — reusable `app-ci@main`
- `main.yml` — Deploy: `deploy-app@<latest tag>`, Tailscale-SSH ohne `ssh_private_key`, `IMAGE_NAME` aus `project.yaml`
- `staging-health.yml`
- Alte SSH-Key-/Legacy-Wiring entfernen

### `project.yaml`
- `environments` (production/staging/local) mit korrekten Domains
- `image_name` = echter ghcr-Pfad (`ghcr.io/bigler-webapps/<app>-backend`)  
  **NIE Platzhalter** `your-org` / `ihr-user` — sonst Image-Kollision auf geteilten Servern
- `app_env`-Block (nicht-geheime Runtime-Config), `version:` (Release-Disziplin)
- **Lokale Ports:** NN aus dem zentralen Register wählen und dort eintragen —
  `webapp-management/docs/LOCAL_PORTS.md`. Nicht raten/wiederverwenden: drei Apps sind
  bereits unabhängig auf dieselbe NN gelandet, weil das Template selbst früher einen
  echten, bereits vergebenen Default auslieferte.
- **Social Login** — Client-IDs sind nicht-geheim, gehören in `app_env` (ein geteilter Client für alle Apps):

  ```yaml
  app_env:
    # ...
    GOOGLE_CLIENT_ID: "585298874656-8r2osbe2mpuah9odf8g15l0nsikvmq1a.apps.googleusercontent.com"
    MICROSOFT_CLIENT_ID: "f107a674-af2d-457f-b50f-3fb0d820c553"
    MICROSOFT_TENANT_ID: common
  ```

### Dockerfile / Compose
- Mit Template abgleichen, damit der `deploy-app`-Build greift.

---

## Phase 2 — dcm + ui-core (Auth kommt automatisch mit)

- **Pins:**
  - `backend/requirements.txt` → `django-core-micha==<current>`
  - `frontend/package.json` → `@micha.bigler/ui-core-micha==<current>`

- **`settings.py`** erbt `dcm settings_base`: Auth-Backends, headless Allauth, DRF default `IsAuthenticated`,  
  `LocaleMiddleware`/i18n, `SECURE_*`. Nur app-spezifische Overrides ergänzen.

- **`urls.py`** — S106: kein klassischer `/accounts/`-Mount; `django_core_micha.api_urls` einbinden.  
  Damit sind `/api/accounts/google/login/callback/` und `/api/accounts/microsoft/login/callback/` automatisch aktiv — kein separater URL-Eintrag nötig.

- **WS-Consumer** — S112: `BaseSecureConsumer` als erste Mixin, `permission_classes_ws`, Logik in `post_connect()`;  
  `test_ws_inventory.py` mit `assert_all_consumers_secure([...])`.

- **`test_permission_inventory.py`** vorhanden (kein ungeschützter Endpoint).

- **Social Login — `secrets.yaml`:**  
  Secrets zeigen auf den **geteilten** Proton-Eintrag in `webapp-management` — kein eigenes Vault-Item anlegen:

  ```yaml
  # Social Auth — secrets only; client_id/tenant_id sind nicht-geheim (project.yaml app_env)
  # WICHTIG: source zeigt auf den gemeinsamen webapp-management-Eintrag, NICHT auf ein per-App-Vault-Item.
  GOOGLE_SECRET:
    source: "proton://webapp-management/social-login/google_client_secret"
    dev_default: ""

  MICROSOFT_SECRET:
    source: "proton://webapp-management/social-login/azure_client_secret"
    dev_default: ""
  ```

- Verifizieren: Boot + echter Login-Flow (headless allauth, inkl. Social Login).

---

## Phase 3 — Umfeld-Registrierung — Checkliste

- [ ] **GitHub-Repo** in der Org (aus/angeglichen an Template), Default-Branch + `develop` vorhanden.
- [ ] **GitHub-Environments** `staging` + `production` angelegt.
- [ ] **Secrets** — eine Ebene pro Secret (`env`-variabel → env; geteilt → repo via `target_scope: repo`).  
  `sync-secrets --server --secret-target <env>` pro Environment + repo-level;  
  danach Timestamps geprüft und keine Shadows (Secret nicht doppelt repo+env).
- [ ] **`inventory.yaml`:** App in `sync_staging_apps` des Ziel-Servers.
- [ ] **DNS (Terraform):** `staging-<app>.<zone>` A-Record + Prod-Domain CNAME→Tunnel (in der `zone-.tf`).  
  Wildcard-first bei evtl. Origin-Cert (Order-Churn vermeiden). `apply`.
- [ ] **CF-Tunnel-Ingress:** der Server-Tunnel routet die App-Hostnames → `traefik:443`.
- [ ] **Kuma-Monitore:** App in `kuma-sync.yml` APPS-Liste + `project.yaml`-Domains  
  (Monitor wird aus `domains[0]` abgeleitet); kuma-sync laufen lassen.
- [ ] **Origin-Cert** (falls eigene Zone, kein Wildcard-Cover): `TF origin-cert-<zone>.tf` (sensitive outputs) → Proton → sync → `dynamic/origin-certs.yml`.
- [ ] **CF Access** (falls Gating nötig, z. B. Dashboard/sensible Endpunkte): `cf-access-<zone>.tf`.
- [ ] **deploy-app-Pin** = aktueller Tag.

### Social Login — Redirect-URIs registrieren

> `sync-secrets` aus dem Secrets-Schritt oben deckt `GOOGLE_SECRET` und `MICROSOFT_SECRET` bereits ab.
> Zusätzlich müssen die **Redirect-URIs** für die neue App beim geteilten OAuth-Client registriert werden.

- [ ] **Azure — `webapp-auth`** (PowerShell, scriptbar):  
  Tenant: `a4cc2b66-c03f-460b-92b4-ec6cee68f0bc` → erst einloggen:
  ```powershell
  az login --allow-no-subscriptions --tenant a4cc2b66-c03f-460b-92b4-ec6cee68f0bc
  ```
  Dann aktuelle URI-Liste lesen (`--web-redirect-uris` **ersetzt die gesamte Liste** — vorher auslesen!):
  ```powershell
  az ad app show --id f107a674-af2d-457f-b50f-3fb0d820c553 --query "web.redirectUris" --output tsv
  ```
  Neue URIs an die bestehende Liste anhängen und die vollständige Liste übergeben:
  ```powershell
  az ad app update --id f107a674-af2d-457f-b50f-3fb0d820c553 --web-redirect-uris `
    <alle-bisherigen-URIs> `
    "https://<prod-domain>/api/accounts/microsoft/login/callback/" `
    "https://<staging-domain>/api/accounts/microsoft/login/callback/"
  ```
  > Hinweis: `az` ist nur in PowerShell verfügbar, nicht in bash/WSL.

- [ ] **Google Console — `webapp-auth`** (manuell, keine API verfügbar):  
  APIs & Services → Credentials → `webapp-auth` → Edit → **Authorized redirect URIs** → Hinzufügen:
  - `https://<prod-domain>/api/accounts/google/login/callback/`
  - `https://<staging-domain>/api/accounts/google/login/callback/`

  > Google OAuth 2.0 Web Application-Clients haben keine öffentliche Management-API  
  > (Google Issue Tracker #182710613, seit 2019 offen). Console ist der einzige Weg.

---

## Phase 4 — End-to-End-Validierung

- **Lokal:** Migrationen + Boot (`/admin/`, Frontend), pytest (permission-inventory + ws-inventory + App-Tests) grün.
- **Push `develop`** → Staging-Deploy → Smoke:
  - `curl https://staging-<app>.<zone>/api/healthz` = 200
  - Login-Flow funktioniert (inkl. Social Login: Google + Microsoft)
  - Container fährt eigenes Image (`docker inspect … {{.Image}}` — kein Platzhalter)
- **Kuma-Monitor** grün.
- **Prod** via `develop→main`-PR (Release-Disziplin: `version:`-Bump + Release Notes; nach Merge Tag `vX.Y.Z` + GitHub Release).

---

## Phase 5 — Cleanup / Drift-Guard

- Legacy-Reste entfernen: alte SSH-Wiring, Platzhalter-Image-Namen, `/accounts`-Mount, tote Deps.
- Keine env/repo-Secret-Shadows (Phase 3 verifizieren).
- Abweichungen vom Template dokumentieren (warum), damit der nächste Drift-Check sie nicht fälschlich flaggt.

---

## Constraints (weil teuer gelernt)

| Constraint | Begründung |
|---|---|
| `IMAGE_NAME` echt, nie Platzhalter | `your-org`/`ihr-user` → Image-Kollision auf geteilten Servern |
| Secret eine Ebene (`target_scope`) | Doppelte repo+env-Shadows sind schwer zu debuggen |
| Kein Feature-Branch | Parallele Agent-Sessions kollidieren im Working-Tree |
| `sync-secrets`-Scope = was der Deploy liest | Falsche Targets → Container bekommt altes Secret |
| Nach Repo/Org-Transfer alle Env-Secrets neu syncen | Secrets hängen am alten Repo |
| Social Login: NIE neue per-App OAuth-Clients | Ein geteilter `webapp-auth` für alle Apps; URIs addieren, nie neu anlegen |
| `az ad app update --web-redirect-uris` liest erst, dann schreibt | Ersetzt die gesamte Liste — aktuelle Liste via `az ad app show` holen |
| Google OAuth: Console only | Keine öffentliche REST-API (Google Issue #182710613, seit 2019 offen) |
| `sync-secrets` ZUERST, dann Deploy | Race: neues CLIENT_ID im Commit-Diff, altes SECRET noch im GitHub-Env → 401 auf OAuth-Callback |
| `gh workflow run --ref develop` | Ohne `--ref` deployt GitHub vom Default-Branch `main` — der enthält noch alte Werte |
