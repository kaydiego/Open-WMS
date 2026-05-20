# Architektur-Übersicht

## Schichtenmodell

```
┌─────────────────────────────────────────────────────────┐
│  Fastlog-eigene UI / Reports / Schnittstellen           │  ← unser Code
│  addons/fastlog_wms/views, reports, controllers          │
├─────────────────────────────────────────────────────────┤
│  Fastlog-Geschäftslogik & Erweiterungen                  │  ← unser Code
│  addons/fastlog_wms/models                                │
├─────────────────────────────────────────────────────────┤
│  Odoo `stock`-Domänenmodell                              │  ← Upstream (LGPL)
│  stock.move, stock.quant, stock.picking, stock.lot, …    │
├─────────────────────────────────────────────────────────┤
│  Odoo-Framework (ORM, Web, Mail, Security)               │  ← Upstream (LGPL)
├─────────────────────────────────────────────────────────┤
│  PostgreSQL 15                                           │  ← Infrastruktur
└─────────────────────────────────────────────────────────┘
```

## Erweiterungsmuster

Drei Wege, um an die Odoo-Datenmodelle "anzudocken":

1. **Bestehendes Modell um Felder erweitern** — `_inherit = 'stock.move'`,
   zusätzliche `fields.Char/Many2one/…` deklarieren.
   Beispiel: `addons/fastlog_wms/models/stock_warehouse.py`.

2. **Bestehendes Modell um Methoden erweitern** — `_inherit` plus
   überschriebene Methode mit `super()`-Aufruf. So lässt sich z. B. das
   Verhalten von `stock.picking._action_done()` ergänzen.

3. **Neues Modell anlegen** — `_name = 'fastlog.…'`. Verweise auf
   Standard-Odoo-Modelle über `Many2one('stock.warehouse', …)`.
   Beispiel: `addons/fastlog_wms/models/fastlog_wms_config.py`.

## Datenflüsse — was wir NICHT anfassen

- Der reine Buchungsfluss `stock.move → stock.move.line → stock.quant`
  bleibt Standard-Odoo. Wir erweitern, ersetzen ihn aber nicht. So
  bleiben Upgrades verträglich.
- Sicherheits- und Zugriffsschicht (`ir.model.access`, Record Rules)
  von Odoo wird weiterverwendet; Fastlog-spezifische Rechte werden
  zusätzlich definiert.

## Testbarkeit

Odoo bringt ein eigenes Test-Framework (`odoo.tests.common.TransactionCase`).
Unsere Tests landen unter `addons/fastlog_wms/tests/` und laufen via:

```bash
docker compose exec odoo odoo \
    -d <dbname> --test-enable --stop-after-init -i fastlog_wms
```
