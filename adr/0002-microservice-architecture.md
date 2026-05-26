# ADR-0002: Microservice-Architektur mit Anti-Corruption-Layer

**Status:** Vorgeschlagen
**Datum:** 2026-05-26
**Entscheider:** Fastlog Engineering

## Kontext

Mit ADR-0001 ist Odoo als reiner Datenunterbau gesetzt. Offene Frage:
Wie strukturieren wir die Anwendungslogik darüber? Optionen reichen
von „modularer Monolith" bis zu „feingranulare Microservices".

Anforderungen:

- Unabhängiges Deployment einzelner Lagerprozesse (Picking-Bugfix soll
  Wareneingang nicht stoppen).
- Klare Eigentümerschaften für Code und Daten.
- Skalierung der Last-Pfade getrennt (Picking-Stosszeiten ≠ Reporting-
  Last).
- Möglichkeit, einzelne Services in anderen Sprachen umzusetzen, wenn
  begründet.
- Secure-by-Design: kleine Trust Boundaries, klare Auditierbarkeit.

## Entscheidung

Wir bauen das Fastlog-WMS als **Microservice-System mit grobem
Domain-Schnitt**:

- **Services initial**: `inbound`, `outbound`, `inventory`,
  `masterdata`, `reporting`, `notify`, `gateway`.
- **Default-Sprache**: Python 3.12 + FastAPI. Polyglot-Wechsel
  (z. B. Go für Gateway) nur mit ADR.
- **Anti-Corruption-Layer** als eigener Service (`acl-odoo`) oder
  geteilte Library im `inbound`/`outbound`/`inventory`-Service.
  Entscheidung Service vs. Library → siehe „Offene Punkte".
- **Kommunikation**:
  - synchron: HTTP/JSON, OpenAPI-First
  - asynchron: NATS JetStream, AsyncAPI-First, Outbox-Pattern
- **Datenhaltung**: Odoo-DB ist Single Source für Bestand. Jeder
  Service hat zusätzlich eine eigene Postgres-DB für seinen
  Prozess-State.
- **Keine** Cross-Service-Joins; Daten anderer Services kommen über
  Events und lokale Projektionen.

## Begründung

- **Klare Fachgrenzen** vermeiden „Big Ball of Mud" – jeder Service
  hat einen erkennbaren Bounded Context.
- **Unabhängige Deploys** sind im Lagerbetrieb wichtig: ein Hotfix
  in Picking darf die Versand-Abendwelle nicht aufhalten.
- **Skalierung** einzeln pro Pfad (Stosszeiten).
- **Audit/Trust Boundaries**: kleinere Services mit klaren APIs sind
  leichter zu modellieren (STRIDE) und zu auditieren.
- **Hiring**: Python + FastAPI ist breit vertraut.

## Alternativen

| Alternative                | Pro                                | Contra                                          | Verworfen weil                                 |
|---------------------------|------------------------------------|-------------------------------------------------|------------------------------------------------|
| Modularer Monolith        | Einfacher Start, weniger Ops       | Schlechte unabhängige Deploys, gemeinsame DB    | Widerspricht Skalierungs- und Trust-Anforderung|
| Feingranulare Microservices (10+) | Maximale Entkopplung      | Hohe Ops-/Netzwerk-Kosten, verteilte Tx schwer  | Overkill für Initial-Team                      |
| Service-pro-Use-Case      | Sehr fokussiert                    | Explodierende Anzahl Services                   | Zu früh                                        |

## Konsequenzen

### Positiv
- Saubere Domain-Grenzen
- Skalierung und Deployment getrennt
- Polyglot-Option bleibt offen
- Audit-/Compliance-freundlich

### Negativ / Risiken
- Mehr Ops-Aufwand (Observability, Deployment-Automatisierung,
  Schema-Registries) – muss bewusst eingeplant werden.
- Verteilte Konsistenz erfordert Disziplin (Outbox, Idempotenz,
  Saga-Light).
- Latenz über Service-Hops; daher BFF-Pattern am Gateway.

### Folgeentscheidungen
- ADR-Wahl Message-Broker (NATS vs. RabbitMQ vs. Kafka) → offen
- ADR-Wahl API-Gateway (Kong vs. Traefik vs. Eigenbau) → offen
- ADR Service- vs. Library-Variante des ACL → offen
- ADR Hosting (K8s vs. Nomad vs. Managed) → offen

## Offene Punkte

- [ ] Festlegung ACL als Service oder Library (Empfehlung: starten als
      Library, extrahieren wenn unabhängige Skalierung nötig wird)
- [ ] Festlegung Broker (Empfehlung: NATS JetStream)
- [ ] Festlegung Gateway-Lösung
- [ ] Festlegung Hosting-Plattform
