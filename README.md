# Fastlog WMS auf Odoo – Dokumentations-Set (Entwurf)

Dieser Ordner ist ein **Vorschlag** für die Architektur- und Projekt-
Dokumentation des neuen Fastlog-WMS auf Odoo-Basis. Die Inhalte sind so
geschrieben, dass sie 1:1 in das künftige eigenständige Repository
(`primelog-odoo` o. ä.) übernommen werden können.

## Lesereihenfolge

1. `CLAUDE.md` – Projekt-Guide für Claude Code, kompakt
2. `ARCHITECTURE.md` – Gesamtbild, Schichten, Microservices, Anti-Corruption-Layer
3. `adr/0001-odoo-as-data-backbone.md` – Warum Odoo nur als Datenunterbau
4. `adr/0002-microservice-architecture.md` – Service-Schnitt
5. `adr/0003-custom-frontend.md` – Warum eigenes UI statt Odoo-Web
6. `SECURITY.md` – Secure-by-Design, Authn/Authz, Audit, Mapping auf Fastlog-KI-Policy
7. `FRONTEND.md` – UI-Stack, Design System, PWA für Lager-Scanner
8. `API-GUIDELINES.md` – Standards für synchrone APIs und Events
9. `GLOSSARY.md` – einheitliche Begriffe DE/EN

## Status

Entwurf. Inhalte abgleichen mit:

- Fastlog KI-Nutzungspolicy V1.0
- Legal / CISO Freigabe für Odoo Community LGPL-3.0
- Endgültige Lizenzwahl für Fastlog-Code

## Nicht im Set

- Konkrete Produkt-Roadmap → gehört ins Backlog, nicht in Architektur-Docs
- Operative Runbooks → kommen mit dem Hosting-Konzept
