# ARCHITECTURE.md – Fastlog WMS auf Odoo

## Vision

Wir bauen ein modernes, modulares WMS. Odoo dient ausschliesslich als
**Datenunterbau** für Bestand und Buchungen – nicht als Anwendungs-
plattform. Geschäftslogik, Workflows, Integrationen und UI bauen wir
**eigenständig** in einer Microservice-Architektur. Eigene UI, weil
die Odoo-Web-UI für Lagerbetrieb und Fastlog-spezifische Prozesse
ungeeignet ist.

Analog: So wie Business Central heute das Datenfundament für Primelog
liefert, übernimmt Odoo diese Rolle für die neue Generation – nur
moderner, offener und ohne Lizenz-pro-User-Kosten.

## Leitprinzipien

1. **Headless Odoo.** Odoo-Web-UI wird **nicht** Endanwendern exponiert.
   Sie bleibt ausschliesslich als Admin/Backoffice-Notnagel verfügbar
   und ist netzwerkseitig auf interne Admin-IPs beschränkt.
2. **Anti-Corruption-Layer (ACL).** Alle Services sprechen Odoo
   ausschliesslich über einen dünnen Adapter an. Odoo-Konzepte
   (`stock.move`, `stock.quant`, externe IDs) lecken nicht in die
   Service-APIs oder ins Frontend.
3. **Domain-getriebene Service-Grenzen.** Jeder Service besitzt ein
   abgegrenztes Geschäfts-Subdomain (Inbound, Outbound, Inventory,
   …) und seinen Prozess-State.
4. **Source of Truth für Bestand: Odoo.** Doppelte Buchhaltung ist
   verboten. Wenn ein Service Bestand verändert, geht das über den
   ACL und letztlich über `stock.move`.
5. **Verträge zuerst.** OpenAPI für synchrone APIs, AsyncAPI für
   Events. Schemata liegen in `shared/contracts/`, Code wird daraus
   generiert (Server- und Client-Stubs).
6. **Secure by Design, Privacy by Default.** Siehe `SECURITY.md`.
7. **Beobachtbarkeit ab Tag 1.** OpenTelemetry-Tracing, strukturiertes
   Logging, Prometheus-Metriken, Error-Tracking.

## Schichten

```
┌──────────────────────────────────────────────────────────────────┐
│ Endgeräte: Desktop-Browser, Handscanner (Android-PWA)            │
├──────────────────────────────────────────────────────────────────┤
│ Frontend                                                          │
│  Next.js Web-App (Backoffice)  │  Scanner-PWA (Floor)             │
├──────────────────────────────────────────────────────────────────┤
│ Edge                                                              │
│  API-Gateway / BFF  (AuthN, Rate-Limit, Routing, Aggregation)     │
├──────────────────────────────────────────────────────────────────┤
│ Services (jeweils eigene DB für Prozess-State)                    │
│  inbound │ outbound │ inventory │ masterdata │ reporting │ notify │
├──────────────────────────────────────────────────────────────────┤
│ Integration                                                       │
│  Anti-Corruption-Layer  ←→  Event-Bus (NATS JetStream)            │
├──────────────────────────────────────────────────────────────────┤
│ Datenunterbau (headless)                                          │
│  Odoo 17 Community  (nur stock + product + Minimal-Addon)         │
├──────────────────────────────────────────────────────────────────┤
│ Persistenz                                                        │
│  PostgreSQL (Odoo)  │  PostgreSQL (pro Service)  │  Objekt-Store  │
└──────────────────────────────────────────────────────────────────┘
```

## Service-Schnitt (initial)

| Service     | Verantwortung                                     | Schreibt nach Odoo? |
|-------------|---------------------------------------------------|---------------------|
| masterdata  | Artikel, Partner, Locations, Lots                 | ja (Spiegel + Pflege) |
| inbound     | ASN, Wareneingang, QS, Putaway-Orchestrierung     | ja (Receipts)       |
| outbound    | Auftrag, Wave, Pick, Pack, Versand                | ja (Deliveries)     |
| inventory   | Bestandsabfrage, Inventur, Umlagerung             | ja (Counts/Moves)   |
| reporting   | Read-Modelle, KPI, Suche (CQRS-Read-Seite)        | nein (read-only)    |
| notify      | E-Mail, Webhook, Push für Scanner                 | nein                |
| gateway/BFF | AuthN-Check, Routing, Frontend-spezifische DTOs   | nein                |

Service-Sprache: **FastAPI in Python 3.12** als Default. Go optional
für I/O-lastige Services (z. B. Gateway, notify), wenn nachweislich
Performance-Bedarf besteht. **Polyglot bewusst minimal halten.**

## Anti-Corruption-Layer

Der ACL ist ein eigener kleiner Service (oder eine Library, die im
ACL-Service läuft, je nach Skalierungsbedarf). Verantwortlich für:

- Übersetzung Domain-DTO ↔ Odoo-Modell
- Authn gegen Odoo (technischer Service-User, Secret aus Vault)
- Retries, Idempotenz-Keys, Circuit-Breaker
- Konsistenz-Garantien (Outbox-Pattern beim Schreiben)

Zugang zur Odoo-API: **JSON-RPC** (stabiler als XML-RPC, gut typisiert
über Pydantic-Modelle). Direkt-SQL nur in Ausnahmefällen für Read-
Modelle des Reporting-Service, mit eigenem Read-Only-DB-User.

## Synchrone vs. asynchrone Kommunikation

- **Synchron (HTTP/JSON, OpenAPI):** Frontend → Gateway → Service,
  Service → ACL. Innerhalb dieser Kette so wenig Hops wie möglich.
- **Asynchron (NATS JetStream, AsyncAPI):** Service → Service
  (Events, lange Prozesse, Fan-out). Beispiele:
  - `inbound.receipt.completed` → `inventory` aktualisiert Cache,
    `reporting` aktualisiert KPI, `notify` schickt Mail.
  - `outbound.shipment.ready_for_carrier` → externer Adapter (Carrier-
    Integration).

## Datenhaltung

| Datentyp | Wo |
|---|---|
| Bestand, Buchungen, Lot-Stammdaten | Odoo-DB (Single Source of Truth) |
| Prozess-State je Service (z. B. „Wave in Auswahl") | Service-eigene Postgres |
| Read-Modelle für UI | Materialized Views / separate DB im reporting-Service |
| Dateianhänge (Bilder, Signaturen) | S3-kompatibler Objekt-Store |
| Audit-Log | append-only Tabelle + Versand an SIEM |

**Keine** Cross-Service-Joins. Wenn ein Service Daten eines anderen
braucht, wird ein Event konsumiert und lokal projiziert.

## Frontend-Anbindung

Das Frontend kennt **ausschliesslich** das Gateway. Pro Bildschirm
liefert das Gateway ein **bildschirmoptimiertes DTO** (BFF-Pattern).
Damit reduzieren wir Roundtrips und vermeiden, dass das Frontend
mehrere Services orchestriert. Details: `FRONTEND.md`.

## Deployment-Topologie

- **Lokal:** docker-compose, ein Service je Container, NATS, Postgres,
  Odoo.
- **Staging/Prod:** Kubernetes. Jeder Service eigenes Helm-Chart.
  Odoo läuft als Stateful-Set, Postgres als Managed-Service oder
  Operator (Crunchy/Zalando).
- **CI/CD:** GitHub Actions / GitLab CI, signierte Container-Images,
  Trivy-Scan, SBOM (CycloneDX) pro Build, Promotion über Tag.

## Beobachtbarkeit

- Traces: OpenTelemetry, Tempo/Jaeger
- Metriken: Prometheus + Grafana, vier Goldene Signale je Service
- Logs: strukturiert (JSON), Loki/ELK, Korrelations-ID = Trace-ID
- Alerts: SLO-basiert (Verfügbarkeit + Latenz-SLI)

## Was bewusst **nicht** in dieser Architektur ist

- **Eventual-Consistency-Wildwuchs.** Bestand ist strikt konsistent
  (Odoo-Transaktion). Async ist für Side-Effects und Read-Modelle.
- **Saga-Frameworks.** Lange Prozesse werden zunächst pragmatisch
  per Outbox + Idempotenz gelöst, nicht über schwere Saga-Engines.
- **Service-Mesh.** Vorerst Overkill. mTLS via Istio o. ä. erst,
  wenn klar Bedarf besteht.
- **Eigenes Auth-System.** Wir benutzen den Fastlog-IdP, fertig.

## Offene Architektur-Fragen → siehe `adr/`

- ADR-0002: Microservices vs. modularer Monolith zum Start
- ADR-0003: Frontend-Stack
- ADR-0004 (offen): API-Gateway-Wahl
- ADR-0005 (offen): Message-Broker-Wahl (NATS vs. RabbitMQ vs. Kafka)
- ADR-0006 (offen): Hosting (Bare-Metal-K8s, Hyperscaler, Odoo.sh)
