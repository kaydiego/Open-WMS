# ADR-0001: Odoo `stock` als Datenunterbau für das Fastlog-WMS

- **Status:** Vorgeschlagen (wartet auf formelle Freigabe durch Legal/CISO)
- **Datum:** 2026-05-20
- **Entscheider:** TBD (Fastlog Engineering / Legal / CISO)

## Kontext

Fastlog AG möchte ein eigenes Warehouse-Management-System aufbauen, ohne
das Datenmodell und die Bestandslogik von Grund auf neu zu entwerfen.
Untersucht wurden vier Open-Source-WMS-Kandidaten:

| Kandidat | Stack | Lizenz | Eignung |
|---|---|---|---|
| OpenBoxes | Grails/Groovy, MySQL/PostgreSQL | EPL-1.0 | Solide, aber Stack altert |
| myWMS LOS | Java EE, PostgreSQL | AGPL-3.0 | Fachlich top, Lizenz für kommerzielles Closed-Source-Produkt problematisch |
| GreaterWMS | Django/Vue, MySQL | AGPL-3.0 | Modern, gleiche Lizenzhürde wie myWMS |
| **Odoo `stock`** | Python, PostgreSQL | LGPL-3.0 | Reifstes Modell, kommerziell verträgliche Lizenz |

## Entscheidung

Wir setzen auf das **Odoo Community `stock`-Modul (Version 17.0)** als
Datenunterbau. Das Fastlog-WMS wird als **eigenständiges Odoo-Addon** unter
`addons/fastlog_wms/` realisiert.

Odoo Community wird **nicht** in dieses Repository vendoriert. Stattdessen
wird zur Laufzeit das offizielle Docker-Image `odoo:17` verwendet und unser
Addon-Verzeichnis über einen Bind-Mount eingehängt.

## Begründung

1. **Datenmodell-Reife:** `stock.move`, `stock.quant`, `stock.picking`,
   `stock.lot`, `stock.warehouse`, `stock.location` sind seit Jahren in
   produktivem Einsatz bei zehntausenden Firmen und decken alle gängigen
   Lagerprozesse ab.
2. **Lizenz:** LGPL-3.0 erlaubt es, eigene Addons unter beliebiger Lizenz
   zu veröffentlichen, solange Änderungen am `stock`-Modul selbst weiter
   unter LGPL bleiben.
3. **Ökosystem:** Python, PostgreSQL, klare ORM-Abstraktion, riesiges
   Pool an Entwicklern und Drittmodulen (OCA — Odoo Community Association).
4. **Wartbarkeit:** Da wir Odoo nicht forken, sondern als Abhängigkeit
   verwenden, sind Upgrades auf neuere Odoo-Versionen mit überschaubarem
   Aufwand möglich. Unser Code bleibt klein und überschaubar.

## Verworfene Alternativen

- **myWMS LOS / GreaterWMS:** Beide AGPL-3.0. Bei Bereitstellung als
  Netzwerk-Dienst zwingt AGPL zur Offenlegung des gesamten abgeleiteten
  Codes — nicht vereinbar mit einem kommerziellen Fastlog-Produkt.
- **OpenBoxes:** EPL-1.0 wäre lizenzrechtlich unproblematisch, aber der
  Grails-/Groovy-Stack verliert seit Jahren an Bedeutung; Rekrutierung
  und Langzeitwartung sind risikobehaftet.
- **Voll-Vendoring von Odoo (~300 MB) ins Repo:** verworfen wegen Repo-
  Grösse, schwieriger Upgrade-Pfade und fehlendem Mehrwert gegenüber dem
  Docker-Image-Ansatz.
- **Git-Submodule für Odoo:** verworfen wegen bekannter UX-Probleme von
  Submodules in der täglichen Arbeit.

## Konsequenzen

**Positiv**

- Repository bleibt klein und übersichtlich (nur Fastlog-Code).
- Klare Trennung zwischen Upstream (Odoo) und unserem Code.
- Standard-Odoo-Entwicklungsmuster — Onboarding neuer Entwickler einfach.
- Upgrade-Pfad auf zukünftige Odoo-Versionen (18, 19, …) bleibt offen.

**Negativ / Risiken**

- Wir sind an Odoos ORM- und Modul-API gebunden. Breaking Changes bei
  Major-Upgrades von Odoo erfordern Anpassungen in unserem Addon.
- Performance-Eigenheiten von Odoo (z. B. das ORM-Verhalten von
  `stock.quant`) gelten auch für unser Produkt.

## Offene Punkte (vor Produktivnutzung zu klären)

- [ ] **Lizenzfreigabe** für die Verwendung von Odoo Community LGPL-3.0
      als Unterbau durch Fastlog Legal/CISO.
- [ ] **Endgültige Lizenz** für den Fastlog-eigenen Code im Repository
      (proprietär / LGPL / sonstige) festlegen.
- [ ] **Eintrag im KI-/Tool-Katalog** der Fastlog KI-Nutzungspolicy V1.0
      ergänzen, falls Odoo dort noch nicht gelistet ist.
- [ ] **Hosting-Konzept** (eigene VM, Kubernetes, Odoo.sh, …) entscheiden.
- [ ] **DSFA** prüfen, sobald produktive Personendaten (Mitarbeitende,
      Kundenkontakte, Empfänger) verarbeitet werden.
