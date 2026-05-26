# FRONTEND.md – Custom UI

## Warum eigenes UI

Odoo-Web-UI ist für unsere Lagerprozesse, Geschwindigkeitsanforderungen
und das Fastlog-Design nicht geeignet. Wir bauen ein eigenes Frontend
und exponieren die Odoo-UI **nicht** an Endanwender. Siehe
`adr/0003-custom-frontend.md`.

## Zielgruppen und Formfaktoren

| Persona              | Gerät                 | App                  |
|----------------------|-----------------------|----------------------|
| Lager-Manager        | Desktop / Laptop      | Web-App (Backoffice) |
| Schichtleitung       | Tablet                | Web-App responsive   |
| Picker / Empfänger   | Handscanner (Android) | Scanner-PWA          |
| Versand / Admin      | Desktop               | Web-App              |
| Geschäftsleitung     | Desktop / Tablet      | KPI-Dashboard im Web |

## Stack-Vorschlag

| Bereich           | Wahl                                          |
|-------------------|-----------------------------------------------|
| Framework         | **Next.js 15** (App Router) + React 19        |
| Sprache           | TypeScript, `strict: true`                    |
| State (Server)    | TanStack Query                                |
| State (Client)    | Zustand für lokalen UI-State                  |
| Forms             | React Hook Form + Zod                         |
| UI-Components     | shadcn/ui (Radix + Tailwind) – ownable Source |
| Styling           | Tailwind CSS                                  |
| i18n              | next-intl                                     |
| Auth              | OIDC via `oidc-client-ts` oder Auth.js (BFF)  |
| Testing (Unit)    | Vitest + React Testing Library                |
| Testing (E2E)     | Playwright                                    |
| A11y-Audit        | axe-core / Playwright a11y Plugin             |
| Bundling          | Turbopack (Next.js Default)                   |
| Linting/Format    | ESLint (typed) + Prettier                     |
| PWA               | next-pwa für Scanner-Variante                 |
| Charts            | Recharts oder Tremor                          |

**Begründung Next.js**: Server-Components reduzieren Roundtrips zum
BFF, SSR/SSG je Seite wählbar, gutes Hiring-Profil, vertraut für
Web-Devs. **Alternative** SvelteKit wäre technisch schlank, aber
schmaleres Talent-Profil.

## Architektur

- **BFF-Pattern**: Das Gateway liefert bildschirm-optimierte DTOs.
  Das Frontend orchestriert **keine** Services direkt.
- **Server Components** für Datenlade-Logik; Client Components nur
  da, wo Interaktivität nötig ist.
- **API-Client generiert** aus OpenAPI-Schema (`shared/contracts/`)
  via `openapi-typescript` + `openapi-fetch`. Keine handgeschriebenen
  Fetchers.
- **Domain-Modul-Struktur** statt nach Technologie:
  ```
  frontend/web/src/
    app/                    # Next.js Routen
    modules/
      inbound/              # UI + Hooks + Types
      outbound/
      inventory/
      masterdata/
      reporting/
    shared/
      ui/                   # Design-System-Komponenten
      lib/                  # apiClient, auth, telemetry, i18n
  ```

## Scanner-PWA

- Single Codebase mit der Web-App, separate Route `/scanner` mit
  eigenem Layout.
- **Offline-tolerant** für kurze Funklöcher: Service-Worker-Cache,
  Outbox für Buchungen (mit Idempotenz-Key, vom Service akzeptiert).
- **Tastatur-/Wedge-Scanner-Support**: Eingaben gehen über versteckte
  Inputs, Bestätigung per Enter-Suffix (Standard-Wedge-Konfiguration).
- **Kamera-Scanner-Fallback** (z. B. `@zxing/browser`).
- **Grosse Touch-Ziele** (≥ 48 px), Hochkontrast-Theme, Vibration/
  Beep für Erfolg/Fehler.
- **Auto-Logout** nach konfigurierbarer Inaktivität.

## Design-System

- Aufbau auf shadcn/ui, eigenes Theme „Fastlog WMS".
- Tokens (Farben, Spacing, Radius, Typografie) in `tailwind.config.ts`.
- Komponenten in Storybook dokumentiert, mit Visual-Regression-Tests
  (Chromatic oder Playwright-Screenshots).
- Icons: lucide-react. Keine Emoji im UI.

## Accessibility

- Ziel **WCAG 2.2 AA**.
- Tastaturbedienung Pflicht für alle interaktiven Komponenten.
- Screenreader-Tests vor Release (NVDA / VoiceOver).
- Farben mit ausreichendem Kontrast (≥ 4.5:1 Text), nie nur über
  Farbe kommunizieren.
- Form-Felder mit `<label>` und Fehlermeldung verknüpft.

## Internationalisierung

- Default-Sprache: **Deutsch (DE-CH)**.
- Strings ausschliesslich aus `messages/de.json` etc.
- Datums-/Zahlenformate via `Intl`-API.
- Vorbereitung für FR / IT / EN – aber MVP nur Deutsch.

## Sicherheit im Frontend

- **Keine Geschäftslogik im Client.** Validierung jedes Inputs
  zusätzlich serverseitig.
- **CSP** restriktiv, `'unsafe-inline'` verboten – `nonce`-basiert.
- Tokens in `HttpOnly` Cookies (Auth.js / BFF-Session), nie im
  `localStorage`.
- Keine Personendaten in URL-Pfaden / Query-Strings.
- Error-UI zeigt nie Stack-Traces; Korrelations-ID für Support.

## Beobachtbarkeit

- OpenTelemetry-Web-Tracing, Trace-ID an Gateway weitergereicht.
- Real User Monitoring (z. B. Sentry) – ohne Personendaten.
- Web-Vitals (LCP, CLS, INP) als Build-Gate.

## Definition of Done für UI-Tasks

- [ ] Komponente in Storybook
- [ ] Unit-Tests (RTL/Vitest)
- [ ] E2E-Test (Playwright) für mind. eine Happy-Path-Route
- [ ] A11y-Check grün
- [ ] i18n-Keys statt Hardcoded-Strings
- [ ] Bundle-Size-Diff geprüft
