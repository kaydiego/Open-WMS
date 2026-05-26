# ADR-0001: Odoo Community als reiner Datenunterbau

**Status:** Vorgeschlagen (wartet auf Legal/CISO-Freigabe)
**Datum:** 2026-05-20 (übernommen aus Vorab-Entscheid)
**Entscheider:** Fastlog Engineering / Legal / CISO

## Kontext

Fastlog möchte ein eigenes Warehouse-Management-System aufbauen, ohne
das Datenmodell und die Bestandslogik von Grund auf neu zu entwerfen.
Bestehender Vergleich (OpenBoxes, myWMS LOS, GreaterWMS, Odoo stock):
Odoos `stock`-Modul ist das reifste und lizenzrechtlich verträglichste
Modell (LGPL-3.0).

## Entscheidung

Wir verwenden **Odoo Community 17.0**, beschränkt auf das
`stock`- und `product`-Modul, ausschliesslich als **Datenunterbau**.

- Odoo läuft headless. UI, Reports, Mail-Workflows werden Endanwendern
  **nicht** exponiert.
- Eigene Anwendungslogik, Workflows und UI liegen in eigenständigen
  Microservices und einem eigenen Frontend (siehe ADR-0002, ADR-0003).
- Odoo wird **nicht** ins Repository vendoriert. Laufzeit über das
  offizielle Docker-Image `odoo:17`; unser Minimal-Addon
  `fastlog_core` wird per Bind-Mount eingehängt.
- Zugriff auf Odoo ausschliesslich über einen Anti-Corruption-Layer.

## Begründung

- **Datenmodell-Reife**: `stock.move`, `stock.quant`, `stock.picking`,
  `stock.lot`, `stock.warehouse`, `stock.location` decken Lagerprozesse
  produktiv erprobt ab.
- **Lizenz**: LGPL-3.0 erlaubt eigene Addons unter eigener Lizenz,
  solange Änderungen am Modul selbst LGPL bleiben.
- **Ökosystem**: Python + PostgreSQL, klare ORM-Abstraktion, OCA-Pool.
- **Upgradepfad**: Da wir Odoo nicht forken, sind Major-Upgrades
  möglich.
- **Kein UI-Lock-in**: Indem wir Odoo headless betreiben, sind wir
  von der Odoo-UI entkoppelt und können sie ohne fachliche Folgen
  ablösen, sollte sich das Datenfundament später ändern.

## Alternativen

| Alternative                | Pro                              | Contra                                                  | Verworfen weil                             |
|---------------------------|----------------------------------|---------------------------------------------------------|--------------------------------------------|
| myWMS LOS / GreaterWMS    | Fachlich gut                     | AGPL-3.0                                                | Lizenz unverträglich mit kommerz. Produkt  |
| OpenBoxes                  | EPL-1.0 OK                       | Grails/Groovy alternder Stack                          | Wartungs- und Personalrisiko               |
| Eigenes Datenmodell        | Volle Freiheit                   | Hoher Aufwand, hohes Risiko                            | ROI niedrig                                |
| Odoo voll-vendoriert       | Reproduzierbarkeit               | ~300 MB Repo, Upgrade-Friktion                         | Bind-Mount + Image deckt Bedarf            |
| Odoo via Git-Submodule     | Reproduzierbarkeit               | Schlechte UX, Verwirrung                                | Bekannte Submodule-Probleme                |

## Konsequenzen

### Positiv
- Repo klein, klare Trennung Upstream/Eigenanteil
- Schnelles Onboarding über Standard-Odoo-Wissen
- Upgrade-Pfade offen

### Negativ / Risiken
- Kopplung an Odoos ORM/Modul-API
- Performance-Eigenheiten (z. B. `stock.quant`) gelten für uns
- ACL muss diszipliniert gepflegt werden, sonst Leak von Odoo-Konzepten

### Folgeentscheidungen
- ADR-0002: Service-Schnitt
- ADR-0003: Custom Frontend
- ADR-noch-zu-schreiben: Hosting, Broker-Wahl

## Offene Punkte

- [ ] Legal/CISO-Freigabe Odoo LGPL-3.0
- [ ] Lizenz Fastlog-eigener Code (proprietär / LGPL / andere)
- [ ] Eintrag im KI-Tool-Katalog
- [ ] Hosting-Konzept
- [ ] DSFA vor Produktivnutzung
