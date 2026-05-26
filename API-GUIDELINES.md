# API-GUIDELINES.md

Gilt für alle synchronen HTTP-APIs (Gateway + Services) und asynchronen
Events. Verträge zuerst, Code danach.

## Synchrone APIs (HTTP / JSON)

### Versionierung

- URL-Versionierung: `/v1/...`. Breaking Changes → `/v2/...`.
- Deprecations werden 6 Monate parallel betrieben, mit `Deprecation`-
  und `Sunset`-Header.

### Ressourcen-Design

- Substantive, Plural: `/v1/receipts`, `/v1/picklists`.
- Aktionen, die nicht REST-konform sind, als Sub-Ressource oder
  Command: `POST /v1/receipts/{id}/complete`.
- IDs sind serverseitig generierte UUIDv7 (zeitsortierbar).

### Methoden

| Methode | Zweck                       | Idempotent? |
|---------|-----------------------------|-------------|
| GET     | Lesen                       | ja          |
| POST    | Anlegen / Command           | nein (Idempotency-Key Header optional) |
| PUT     | Vollständig ersetzen        | ja          |
| PATCH   | Teilweise ändern (JSON Patch oder Merge Patch, dokumentieren!) | ja |
| DELETE  | Löschen                     | ja          |

### Idempotenz

- `Idempotency-Key`-Header auf allen schreibenden Endpunkten, die
  Geld/Bestand bewegen. Server speichert (Key, Response) für 24 h.

### Pagination

- Cursor-basiert: `?limit=50&cursor=...`. Response:
  ```json
  {
    "data": [...],
    "page": { "next_cursor": "abc", "limit": 50 }
  }
  ```
- Offset-Pagination ist verboten (Performance).

### Filtering / Sortierung

- Filter als Query-Param: `?status=done&warehouse_id=FL01`.
- Sortierung: `?sort=created_at,-priority` (Minus = absteigend).

### Fehlerformat

**Problem Details for HTTP APIs (RFC 9457)** ist Pflicht:

```json
{
  "type": "https://errors.fastlog.example/wms/receipt/qc-failed",
  "title": "QC failed",
  "status": 422,
  "detail": "Receipt RC-00042 hat fastlog_qc_status=failed.",
  "instance": "/v1/receipts/RC-00042/complete",
  "request_id": "01HXYZ..."
}
```

- `type` ist stabile URL pro Fehlerklasse.
- Keine Stack-Traces in Production-Antworten.

### Statuscodes

- 200 OK, 201 Created (mit `Location`), 202 Accepted (async)
- 204 No Content für DELETE
- 400 Bad Request (Validierung), 401 Unauthorized, 403 Forbidden,
  404 Not Found, 409 Conflict, 422 Unprocessable Entity (fachlich)
- 429 Too Many Requests
- 5xx nur bei tatsächlichen Server-Fehlern

### Headers

- `X-Request-Id` durchreichen / generieren
- `traceparent` (W3C Trace Context)
- `Content-Type: application/json; charset=utf-8`
- `Accept-Language` respektieren (i18n der Fehlermeldungen)

### Auth

- OAuth2 / OIDC Bearer-Tokens, kurz lebig.
- Scopes pro API dokumentiert.
- mTLS zwischen internen Services.

### Rate Limiting

- Standard 60 req/s/User am Gateway, Burst 120.
- Header: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`.

### Doku

- OpenAPI 3.1 pflichtig. Quelle: `shared/contracts/openapi/<service>.yaml`.
- Aus dem Schema werden Server-Stubs (FastAPI) und Client (TS) generiert.
- Beispiel-Requests/-Responses für jede Operation.

## Asynchrone Events

### Transport

- **NATS JetStream** als Default. Streams pro Bounded Context.
- Subjects: `fastlog.<domain>.<aggregate>.<event>`, z. B.
  `fastlog.inbound.receipt.completed`.

### Format

- CloudEvents 1.0 + JSON-Body.
- Schema dokumentiert in `shared/contracts/asyncapi/<service>.yaml`.
- Felder pro Event:
  - `id` (UUIDv7)
  - `source` (Service-URN)
  - `type` (`fastlog.inbound.receipt.completed`)
  - `time` (RFC 3339 UTC)
  - `subject` (Aggregate-ID)
  - `data` (Payload, versioniert)
  - `dataschema` (Schema-URL)

### Garantien

- **At-least-once Delivery.** Konsumenten sind idempotent (Event-ID
  in lokaler Outbox-Tabelle prüfen).
- **Ordnung**: nur innerhalb eines Streams + Partitions-Keys, nicht
  global.
- **Outbox-Pattern** beim Publishen: gleiche DB-Transaktion wie der
  fachliche State-Change.

### Versionierung

- Neue Felder additiv. Breaking Change → neuer Event-Type
  (`...completed.v2`), Übergangszeit beide.

### Doku

- AsyncAPI 3.0 pflichtig.

## Allgemein

- **Naming**: `snake_case` in JSON-Payloads (konsistent mit Python/SQL).
- **Zeitangaben**: immer UTC, RFC 3339 (`2026-05-26T14:32:00Z`).
- **Geldwerte**: `{ amount: "12.50", currency: "CHF" }` als Strings.
- **Bool-Defaults**: explizit nennen, keine impliziten Defaults.
- **Niemals** interne IDs aus Odoo (numerische DB-IDs) nach aussen
  durchreichen. Wir exponieren fachliche IDs / UUIDs.

## Checkliste vor Endpoint-Merge

- [ ] OpenAPI/AsyncAPI aktualisiert?
- [ ] Beispiele dokumentiert?
- [ ] Fehler nach RFC 9457?
- [ ] Auth-Scope korrekt?
- [ ] Idempotenz bedacht?
- [ ] Pagination konsistent?
- [ ] Rate-Limit gesetzt?
- [ ] Audit-Event ergänzt (bei sicherheitsrelevanten Ops)?
