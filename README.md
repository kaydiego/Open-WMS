# Open-WMS (Fastlog)

Fastlog-WMS auf Basis des Odoo-`stock`-Datenmodells. Dieses Repository enthält
**ausschliesslich** den Fastlog-spezifischen Code als Odoo-Addon. Odoo selbst
wird als externe Abhängigkeit über Docker bereitgestellt — wir vendoren den
Upstream-Code nicht.

## Architektur in einem Satz

Odoo Community Edition liefert das Datenmodell (`stock.move`, `stock.quant`,
`stock.picking`, `stock.lot`, …), das Modul `addons/fastlog_wms` erweitert es
um Fastlog-spezifische Felder, Logik, Views und Reports.

Die ausführliche Begründung steht in
[`docs/adr/0001-odoo-stock-als-datenunterbau.md`](docs/adr/0001-odoo-stock-als-datenunterbau.md).

## Repository-Layout

```
Open-WMS/
├── addons/
│   └── fastlog_wms/          Unser Odoo-Addon (depends = ['stock'])
├── docker/
│   ├── docker-compose.yml    Odoo 17 + PostgreSQL 15 lokal
│   └── odoo.conf
├── docs/
│   ├── adr/                  Architecture Decision Records
│   └── architecture/         Diagramme, Übersichten
├── LICENSE
└── README.md
```

## Lokales Setup

Voraussetzungen: Docker + Docker Compose.

```bash
cd docker
docker compose up -d
# Odoo läuft danach auf http://localhost:8069
# beim ersten Login eine Datenbank anlegen und das Modul "Fastlog WMS" installieren
```

Das Addon-Verzeichnis `../addons` wird per Bind-Mount in den Odoo-Container
gemountet — Änderungen werden nach `docker compose restart odoo` aktiv.

## Beitrag / Workflow

- Entwicklung auf Feature-Branches, Reviews via Pull Request.
- ADRs ergänzen, wenn architektonisch relevante Entscheidungen anstehen.
- **Keine** Personendaten, Kunden- oder Vertragsdaten in Repo oder Issues
  einchecken (siehe Fastlog KI-Nutzungspolicy V1.0, Abschnitt 1).

## Lizenz

Siehe [`LICENSE`](LICENSE). Die endgültige Lizenzwahl für den Fastlog-Anteil
ist durch Legal/CISO freizugeben (siehe ADR-0001, "Offene Punkte").
