# SECURITY.md – Secure by Design

Dieses Dokument legt verbindliche Sicherheits- und Datenschutzprinzipien
für das Fastlog-WMS fest. Es ist Pflichtlektüre für alle Entwickler und
KI-Agenten, die an diesem Repo arbeiten. Bei Konflikten gilt:
**Fastlog KI-Nutzungspolicy V1.0 > revDSG / GDPR > dieses Dokument.**

## Schutzziele (CIA + P)

| Ziel             | Beispiele                                                   |
|------------------|-------------------------------------------------------------|
| Confidentiality  | Kein Leak von Kundendaten, Bestandsmengen, Preisen          |
| Integrity        | Buchungen nur über ACL, signierte Events, Audit-Log         |
| Availability     | Lagerbetrieb darf nicht stehen → SLO + Redundanz            |
| Privacy          | Minimaldatenprinzip, Pseudonymisierung, DSFA bei Bedarf     |

## Threat Modeling

- **STRIDE pro Service** bei jedem grösseren Design-Change (mind. einmal
  pro Quartal). Ergebnisse als ADR oder unter `docs/threat-models/`.
- **Trust Boundaries** explizit dokumentieren: Frontend ↔ Gateway,
  Gateway ↔ Services, Services ↔ ACL ↔ Odoo, intern ↔ Internet.
- Bei sicherheits- oder buchungskritischen Änderungen (Gefahrgut,
  Finanzwerte, Zoll): **4-Augen-Prinzip** wie Fastlog-Policy verlangt.

## Authentifizierung

- **Endanwender:** OIDC gegen Fastlog-IdP (z. B. Keycloak / Entra ID),
  **MFA Pflicht**. Keine lokalen Accounts.
- **Service-zu-Service:** mTLS oder kurze, gescopte JWTs (z. B. OAuth2
  Client Credentials Flow). Tokens nie länger als 1 h.
- **ACL ↔ Odoo:** technischer Service-User in Odoo, Passwort/API-Key
  ausschliesslich in Vault, Rotation alle 90 Tage.
- **Scanner-PWA:** OIDC Authorization Code + PKCE, Refresh-Tokens nur
  in `HttpOnly; Secure; SameSite=Strict` Cookies, Auto-Logout nach
  Inaktivität (Schichtende).

## Autorisierung

- **RBAC** als Basis, ergänzt um **ABAC** wo nötig (z. B. „nur
  Lager-Manager der Niederlassung X dürfen Bestand korrigieren").
- Policies **zentral** im Gateway evaluieren (z. B. OPA/Rego oder
  Casbin), nicht in jedem Service neu erfinden.
- **Least Privilege**: Default-Deny, jede Rolle minimal scoped.
- Trennung sicherheitskritischer Funktionen: wer Bestand bucht, darf
  nicht gleichzeitig Audit-Logs löschen.

## Daten und Datenschutz

- **Klassifizierung** gemäss Fastlog-KI-Tool-Katalog. Pro Tabelle/
  Endpoint dokumentieren: öffentlich / intern / vertraulich /
  besonders schützenswert.
- **Pseudonymisierung** für Test-/Dev-Umgebungen. Echtdaten **nie**
  in nicht-produktive Stages.
- **Personendaten** nur, wenn fachlich zwingend; Rechtsgrundlage
  dokumentieren (Art. 5 revDSG / Art. 6 GDPR).
- **Automatisierte Einzelentscheide mit erheblicher Auswirkung auf
  Personen sind untersagt** (Art. 21 revDSG). Wo KI-Vorschläge
  Personen betreffen, immer mit menschlichem Freigabe-Schritt.
- **Auskunfts-/Löschrechte**: jede Personendatentabelle muss eine
  dokumentierte Lösch- und Export-Funktion haben.

## Geheimnisse

- **Vault** (HashiCorp) oder Kubernetes Sealed Secrets als Single
  Source.
- **Niemals** Secrets in:
  - Code, Tests, Compose-Defaults
  - Commit-Messages, PR-Beschreibungen, Issue-Kommentaren
  - Log-Ausgaben (Filter im Logger)
  - KI-Prompts (siehe Org-Policy)
- Rotation: Service-Tokens 24 h, DB-Passwörter 90 Tage, OIDC-Client-
  Secrets jährlich.

## Eingaben / Schnittstellen

- **Input-Validation** am System-Boundary (Gateway, externe APIs)
  mit Schemata (Pydantic, Zod) – keine Validierung interner
  Aufrufer wiederholen.
- **Output-Encoding** kontextspezifisch (HTML, JSON, SQL via ORM,
  Logs sanitisieren).
- **CSRF** über SameSite-Cookies + Token-Pattern, wo Cookies genutzt
  werden.
- **CORS** restriktiv: nur unsere eigenen Origins.
- **CSP**, HSTS, Referrer-Policy, X-Content-Type-Options, Permissions-
  Policy als Default-Header.

## Sichere Entwicklung (SDLC)

- Pre-Commit: ruff, eslint, gitleaks (Secret-Scan), pre-commit-mypy.
- CI-Pflicht:
  - **SAST** (Semgrep)
  - **SCA** (pip-audit, npm audit / osv-scanner)
  - **Container-Scan** (Trivy/Grype)
  - **IaC-Scan** (tfsec/checkov)
  - **SBOM** (CycloneDX) als Artefakt
- Container: Distroless, non-root, read-only Filesystem, kein `latest`.
- Image-Signatur: Cosign (Sigstore), Verifikation im Cluster.
- Branch-Protection: PR-Review Pflicht, sicherheitskritisch = 2
  Reviewer (4-Augen), Status-Checks grün.

## Audit und Logging

- **Append-only Audit-Log** für sicherheitsrelevante Ereignisse:
  Login, Rollenwechsel, Bestandskorrektur, Stornierung, Massen-
  exporte. Felder: who, when, what, before/after, request-id.
- Versand an zentrales SIEM (z. B. via Loki/Elastic).
- **Datenschutz im Log**: keine vollständigen Personendaten, nur
  IDs / pseudonyme Referenzen.
- Aufbewahrung: 1 Jahr Online, 7 Jahre Archiv (sofern Recht es
  verlangt – mit Legal abstimmen).

## Verfügbarkeit

- SLO pro Service definieren (z. B. 99.5 % Picking-Service während
  Lagerbetriebszeit).
- Health-/Readiness-Probes verpflichtend.
- Backups: Odoo-DB inkrementell stündlich, Full nightly, Restore
  mind. einmal pro Quartal getestet.
- DR-Plan: RPO/RTO pro Datenklasse dokumentieren.

## Lieferkette

- Nur freigegebene Pakete (Mirror / Artifactory).
- Lockfiles in VCS, reproducible builds.
- Renovate/Dependabot mit Sicherheits-Updates auf Auto-Merge nach
  Test-Grün, alles andere manuell.
- Lizenzscan (FOSSA / ScanCode) – Outputs gegen Allowlist prüfen
  (vgl. Fastlog-Policy zu Urheberrecht).

## Vorfallmanagement

- Verdacht auf Datenabfluss, Prompt-Injection, fehlerhafte Outputs:
  **sofortige Meldung an CISO und DSK** (gemäss Fastlog-Policy).
- Runbook unter `deploy/runbooks/incident-response.md`.
- Post-Mortem blameless, Action-Items ins Backlog mit Owner.

## Spezielle Bereiche

- **HR-/Personalbezogene Auswertungen**: nur unterstützend, kein
  automatisches Ranking ohne DSFA und Einspruchsrecht.
- **Gefahrgut / Zoll / Finanzen**: Outputs durch qualifiziertes
  Personal validieren, 4-Augen-Prinzip.
- **Kundenkommunikation**: KI-gestützte Kommunikation kennzeichnen.

## Checkliste vor Merge (Security-Gate)

- [ ] Threat-Model-Auswirkung geprüft?
- [ ] Eingaben am Boundary validiert?
- [ ] Authn/Authz geprüft?
- [ ] Keine Secrets in Code/Logs?
- [ ] Personendaten korrekt klassifiziert und minimiert?
- [ ] Audit-Events ergänzt?
- [ ] SAST/SCA/Container/IaC-Scans grün?
- [ ] Doku / ADR aktualisiert?
