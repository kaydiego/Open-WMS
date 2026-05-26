# CLAUDE.md – Projekt-Guide für Claude Code

Dieses Dokument ist die Quelle der Wahrheit, wenn Claude Code an diesem
Repo arbeitet. Es ergänzt – und unterliegt – der Fastlog-Organisations-
Policy. Bei Widerspruch gilt: Org-Policy > CLAUDE.md > Konversation.

## Projekt in einem Satz

Fastlog WMS ist ein modulares, Microservice-basiertes Warehouse-
Management-System mit eigener UI, das **Odoo Community** ausschliesslich
als **Datenunterbau für Bestand und Buchungen** nutzt – analog zur
Rolle, die Business Central heute für Primelog spielt.

## Architektur in drei Sätzen

1. Odoo läuft headless; nur das `stock`-Domänenmodell und die Buchungs-
   logik werden genutzt. Keine Odoo-UI-Screens, keine Odoo-Reports,
   keine Odoo-Mail-Workflows nach aussen.
2. Eigene Microservices kapseln Fastlog-Logik und sprechen Odoo
   ausschliesslich über einen **Anti-Corruption-Layer (ACL)** an – nie
   direkt aus dem Frontend, nie aus anderen Services.
3. Das Frontend ist eine eigenständige Web-/PWA-App, kommuniziert
   ausschliesslich mit dem **API-Gateway**, nie mit Odoo oder den
   internen Services direkt.

Details siehe `ARCHITECTURE.md`.

## Repo-Struktur (Zielbild)

```
primelog-odoo/
├── services/
│   ├── inbound/          # Wareneingang, Putaway
│   ├── outbound/         # Picking, Packing, Versand
│   ├── inventory/        # Bestand, Inventur, Umlagerung
│   ├── masterdata/       # Artikel, Partner, Locations
│   ├── reporting/        # KPI, Read-Modelle
│   └── gateway/          # API-Gateway / BFF
├── odoo/
│   ├── addons/
│   │   └── fastlog_core/ # Minimal: nur Felder/Methoden, die wir auf
│   │                     # stock.* zwingend brauchen
│   ├── docker/
│   └── docker-compose.yml
├── frontend/
│   ├── web/              # Next.js / React (Hauptanwendung)
│   └── mobile-pwa/       # Scanner-PWA (kann auch im selben Projekt
│                         # über Routen liegen)
├── shared/
│   ├── contracts/        # OpenAPI + AsyncAPI Schemata
│   └── libs/             # gemeinsame Typen / Clients (TS, Python)
├── deploy/               # IaC, Helm-Charts, K8s-Manifeste
├── docs/
│   ├── adr/
│   ├── ARCHITECTURE.md
│   ├── SECURITY.md
│   ├── FRONTEND.md
│   ├── API-GUIDELINES.md
│   └── GLOSSARY.md
└── CLAUDE.md             # dieses Dokument
```

## Goldene Regeln (für Claude und Menschen)

### Was wir tun

- **Odoo so wenig wie möglich modifizieren.** Wo Erweiterung nötig:
  - bestehende Felder via `_inherit` ergänzen
  - Methoden via `super()` erweitern, nicht ersetzen
  - eigene Modelle nur, wo Odoo keine passende Entität hat
- **Geschäftslogik gehört in die Microservices**, nicht in Odoo-Addons.
  Odoo bekommt nur Logik, die für die Datenkonsistenz von `stock.*`
  zwingend nötig ist.
- **Verträge zuerst.** Neue Endpunkte/Events erst als OpenAPI/AsyncAPI
  unter `shared/contracts/` definieren, dann implementieren.
- **Tests bei jedem Change.** Service-Tests + mindestens 1
  Integrationstest, der den Pfad Frontend → Gateway → Service → ACL
  → Odoo abdeckt.
- **Secure by Default.** Siehe `SECURITY.md`.

### Was wir nicht tun

- Keine Odoo-Views, -Menüs oder -Reports für Endanwender bauen.
- Kein direkter DB-Zugriff auf die Odoo-Postgres aus Services oder
  Frontend. Immer über den ACL.
- Keine Geschäftslogik im Frontend, die nicht auch im Backend validiert
  wird.
- Keine Geheimnisse, Personendaten, Kunden- oder Vertragsdaten in
  Prompts, Tests, Demo-Daten, Commits, Logs. Pseudonymisieren.
- Keine Forks von Odoo-Modulen. Nur Inherit/Override im eigenen Addon.
- Kein Bypass von Lints/Hooks (`--no-verify`, `--no-gpg-sign`).
- Keine produktiven Credentials in `.env`, `compose`-Defaults, CI-Logs.
- Keine destruktiven Git-Operationen ohne explizite Aufforderung
  (force-push, reset --hard, branch -D).

## Toolchain

| Bereich | Tools |
|---|---|
| Sprache Services | Python 3.12 + FastAPI (Default), Go für I/O-lastige Services |
| Sprache Frontend | TypeScript, Next.js (React) |
| Datenhaltung | Odoo-Postgres (Bestand/Buchungen), pro Service eigene DB für Prozess-State |
| Messaging | NATS JetStream (Default), Alternative: RabbitMQ |
| API-Gateway | Kong, Traefik oder Eigenbau auf FastAPI – siehe ADR |
| Auth | OIDC via Fastlog-IdP, MFA Pflicht |
| Secrets | HashiCorp Vault oder Kubernetes Sealed Secrets |
| Container | Docker, Distroless-Images wo möglich |
| Orchestrierung | Kubernetes (Hosting-Entscheid offen) |
| IaC | Terraform + Helm |
| Tests | pytest, vitest, Playwright, k6 (Last) |
| Lint/Format | Ruff + Black (Python), ESLint + Prettier (TS), pre-commit |

## Befehle (Soll-Zustand)

```bash
# Entwicklung
make up               # docker compose up für alle lokalen Abhängigkeiten
make down
make logs SERVICE=inbound

# Tests
make test             # alle Tests
make test-service SERVICE=inbound
make test-e2e         # Playwright

# Qualität
make lint
make typecheck
make security         # Trivy / Grype / npm audit / pip-audit

# Odoo-spezifisch (selten nötig)
make odoo-shell
make odoo-test ADDON=fastlog_core
```

## Code-Style Kurzfassung

- Python: Ruff-Default + Black, Type-Hints überall, Pydantic v2 für DTOs
- TypeScript: strict, no implicit any, Zod für Runtime-Validierung
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, …)
- Branches: `feat/<ticket>-<slug>`, `fix/<ticket>-<slug>`
- PRs klein halten, < 400 LOC Diff angestrebt, mind. 1 Review
- Sicherheits- oder buchungskritische Änderungen: **4-Augen-Prinzip**

## Was Claude bei jeder Aufgabe prüfen muss

1. Berührt der Change Personendaten oder Kundendaten? → Pseudonymisieren.
2. Wird Odoo-Verhalten ausserhalb von `stock.*` benötigt? → Halt, ADR
   schreiben, Rückfrage.
3. Wäre die Logik im Service besser aufgehoben als im Odoo-Addon? → Ja,
   meistens.
4. Gibt es einen Contract (OpenAPI/AsyncAPI) für die Schnittstelle? →
   Wenn nein, zuerst Contract.
5. Sind Tests dabei? → Ohne Tests kein Merge.
6. Greift der SECURITY.md-Checkliste etwas? → Abarbeiten.

## Was Claude **nie** ohne Rückfrage tut

- Produktiv-Daten anfassen, auch lesend.
- ADR-Entscheidungen umkehren.
- Neue Top-Level-Verzeichnisse anlegen.
- Externe Dienste anbinden (Carrier-APIs, Cloud-Provider, …).
- Lizenzen ändern oder Dritt-Code mit nicht-kompatibler Lizenz einbinden.

## Verweise

- `ARCHITECTURE.md` – Architekturbild
- `SECURITY.md` – Sicherheitsanforderungen
- `FRONTEND.md` – UI-Konventionen
- `API-GUIDELINES.md` – REST + Event-Standards
- `adr/` – Entscheidungen
- Fastlog KI-Nutzungspolicy V1.0 (intern)
