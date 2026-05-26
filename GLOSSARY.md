# GLOSSARY.md – Fastlog-WMS-Begriffe

Einheitliche Sprache zwischen Fachbereich, Code und API. Bei Konflikten
gilt die hier definierte Bezeichnung.

## Lager-Domäne

| Begriff (DE)            | Begriff (EN / Code)        | Definition |
|-------------------------|----------------------------|------------|
| Lager                   | warehouse                  | Physische oder logische Einheit mit eigenem Bestand. In Odoo: `stock.warehouse`. |
| Standort / Lagerort     | location                   | Logischer Ort innerhalb eines Lagers (Hierarchie). In Odoo: `stock.location`. |
| Lagerfach / Bin         | bin                        | Konkreter Lagerplatz (kleinste Granularität). Wird in `stock.location` mit `fastlog_zone='storage'` und `fastlog_bin_code` abgebildet. |
| Zone                    | zone                       | Funktionale Gruppe von Locations: Receiving, Storage, Picking, Packing, Shipping, Quarantine. |
| Artikel / Produkt       | product                    | In Odoo: `product.product` (Variante) bzw. `product.template`. |
| Charge                  | lot                        | Identifizierbare Produktionsmenge. In Odoo: `stock.lot`. |
| Seriennummer            | serial                     | Stück-eindeutige Charge. Sonderfall von Lot. |
| Bestand                 | stock / quant              | Aktuelle Menge je Produkt × Location × Lot. In Odoo: `stock.quant`. |
| Buchung                 | move                       | Atomare Bestandsbewegung. In Odoo: `stock.move`. |
| Buchungsschritt         | move line                  | Konkrete Ausführung einer Buchung mit Quelle/Ziel/Lot. In Odoo: `stock.move.line`. |
| Lieferschein / Picking  | picking                    | Sammlung von Buchungen für einen Ein-/Aus- oder internen Vorgang. In Odoo: `stock.picking`. |

## Prozesse

| Begriff (DE)            | Begriff (EN / Code)        | Definition |
|-------------------------|----------------------------|------------|
| Avis / Avisierung       | ASN (Advance Shipping Notice) | Voranmeldung Wareneingang. Bei uns: Feld `fastlog_asn_reference` auf Receipt. |
| Wareneingang            | receipt / inbound          | Incoming-Picking + Putaway. |
| Einlagerung             | putaway                    | Zuordnung empfangener Ware zu Storage-Bins. |
| Qualitätskontrolle      | QC                         | Prüfungsschritt während Wareneingang. Status: pending / passed / failed. |
| Kommissionierung        | picking (outbound)         | Entnahme aus Storage für Versand. |
| Wave                    | wave                       | Bündelung mehrerer Aufträge zur effizienten Kommissionierung. |
| Batch                   | batch                      | Bündel von Pickings, die ein Picker zusammen abarbeitet. |
| Packen                  | packing                    | Zusammenstellung kommissionierter Ware in Versandeinheiten. |
| Versand                 | shipment / outbound        | Übergabe an Carrier. |
| Inventur (zyklisch)     | cycle count                | Stichproben-Zählung im Betrieb. |
| Vollinventur            | full count                 | Stichtags-Zählung des Gesamtbestands. |
| Umlagerung              | internal transfer          | Bewegung zwischen Locations ohne Eingang/Ausgang. |
| Sperre / Quarantäne     | quarantine                 | Bestand temporär nicht verfügbar (z. B. Reklamation). |

## Identifikatoren

| Begriff (DE)            | Begriff (EN / Code)        | Definition |
|-------------------------|----------------------------|------------|
| SKU                     | sku                        | Stock Keeping Unit – fachliche Artikelnummer. |
| GTIN / EAN              | gtin                       | Globaler Artikelidentifikator (Barcode). |
| SSCC                    | sscc                       | Serial Shipping Container Code (Paletten-/Karton-ID). |
| Idempotency-Key         | idempotency_key            | Vom Client erzeugter Schlüssel zur Wiederholungssicherheit. |

## Rollen

| Rolle                   | Beschreibung |
|-------------------------|--------------|
| Empfänger (Receiver)    | Erfasst Wareneingang, scannt ASN, dokumentiert QC. |
| Einlagerer (Putaway)    | Bringt Ware vom Receiving in Storage. |
| Picker                  | Entnimmt Ware für Aufträge. |
| Packer                  | Verpackt und labelt Versandeinheiten. |
| Versand                 | Übergibt an Carrier, schliesst Versand ab. |
| Lager-Manager           | Steuert Wellen, korrigiert Bestand (mit Audit), pflegt Stammdaten. |
| QS-Inspektor            | Setzt QC-Status, gibt Sperrungen frei. |
| Admin                   | Konfiguriert Lager, Rollen, Integrationen. |

## Technik

| Begriff                 | Definition |
|-------------------------|------------|
| ACL                     | Anti-Corruption-Layer zwischen unseren Services und Odoo. |
| BFF                     | Backend for Frontend – pro UI-Variante optimierte Aggregations-Schicht. |
| Outbox-Pattern          | Schreiben fachlicher State-Change + Event-Versand in einer DB-Transaktion. |
| Event-Stream            | Append-only Strom domain-bezogener Ereignisse (NATS JetStream). |
| Read-Model              | Für UI/Reporting optimierte Projektion eines Aggregats. |
| Aggregat (DDD)          | Konsistenzgrenze über mehrere Entitäten. |
| Bounded Context         | Fachlich abgegrenzter Bereich mit eigenem Vokabular. |

## Gewollt **nicht** benutzte Begriffe

- „Order" allein – mehrdeutig. Stattdessen `sales_order`, `purchase_order`,
  `picking`, `wave`.
- „Item" allein – mehrdeutig. Stattdessen `product`, `move_line`,
  `picking_line`.
- „Stock" als Buchungssubstantiv – verwirrend mit Bestand. Stattdessen
  `move` für Buchung, `quant` für Bestandsposition.
