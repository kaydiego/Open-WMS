# ADR-0003: Eigenes Frontend, Odoo-Web-UI nicht verwendet

**Status:** Vorgeschlagen
**Datum:** 2026-05-26
**Entscheider:** Fastlog Engineering / Produkt

## Kontext

Odoo bringt eine eigene Web-UI mit. Sie ist für generische ERP-
Backoffice-Arbeit ausgelegt, nicht für hochfrequente Lagerprozesse
mit Scanner, Schichtarbeit, klar definiertem Corporate-Design und
Fastlog-spezifischen Workflows. Erste Sichtung mit Fachbereich: die
Odoo-UI wird als „katastrophe" für die geplante Anwendung bewertet.

Anforderungen ans Frontend:

- Optimiert für Lager-Workflows: wenige Klicks, grosse Touch-Ziele,
  Tastatur-/Scanner-First.
- Eigenes Corporate Design.
- Mobile (Handscanner) und Desktop (Backoffice).
- Offline-Toleranz im Lager.
- Saubere Trennung von der Datenschicht; UI darf Odoo-Konzepte nicht
  zeigen.
- Modernes Hiring-Profil, langfristige Wartbarkeit.

## Entscheidung

Wir bauen ein **eigenes Frontend** und exponieren die Odoo-Web-UI
**nicht** an Endanwender (sie bleibt rein admin-intern, netzwerk-
seitig geschützt).

- **Stack**: Next.js 15 (App Router) + React 19 + TypeScript strict.
- **UI-Komponenten**: shadcn/ui (Radix + Tailwind).
- **Server-State**: TanStack Query; **Forms**: React Hook Form + Zod.
- **Auth**: OIDC gegen Fastlog-IdP, MFA Pflicht.
- **Scanner-Variante**: PWA im selben Repo unter `/scanner`-Routen,
  next-pwa, offline-toleranter Outbox-Mechanismus mit Idempotency-
  Key.
- **Anbindung**: ausschliesslich über das **API-Gateway / BFF** des
  Backends. Generierter TS-Client aus OpenAPI (`shared/contracts/`).

## Begründung

- Odoo-Web-UI ist generisch und passt nicht zu Lager-UX.
- Next.js bietet Hybrid-Rendering, gute DX, breite Talent-Basis.
- shadcn/ui liefert ownable, anpassbare Komponenten ohne Vendor-
  Lock-in.
- PWA reicht für Handscanner (Android-Geräte mit Chrome) – keine
  native App nötig im MVP.
- Strikte Trennung Frontend ↔ Odoo via Gateway/ACL hält den
  Backend-Schnitt sauber.

## Alternativen

| Alternative                | Pro                                | Contra                                                  | Verworfen weil                          |
|---------------------------|------------------------------------|---------------------------------------------------------|-----------------------------------------|
| Odoo Web-UI direkt        | Schnell, „alles aus einer Hand"    | UX schlecht, Lock-in an Odoo-Frontend, kein Eigen-CD    | Widerspricht Anforderung                 |
| Odoo OWL (Custom-Widgets) | Tief integriert                    | Bindet uns an Odoos Frontend-Framework, kleine Community| Lock-in, schwaches Talent-Profil         |
| SvelteKit / Solid-Start   | Schlank, schnell                   | Schmaleres Talent-Profil                                | Hiring-Risiko                            |
| Native Android-App        | Beste Performance Scanner          | Doppelte Codebase, App-Store-Hürden                     | PWA reicht im MVP                        |

## Konsequenzen

### Positiv
- Volle UX-Kontrolle, eigenes Design
- Klare Trennung von Odoo-Lock-in
- Eine Codebase für Desktop und Handscanner
- Modernes Hiring-Profil

### Negativ / Risiken
- Wir tragen den vollen Frontend-Aufwand (was bei Odoo „geschenkt"
  wäre).
- Wir müssen Auth, Auditing, i18n etc. selbst sauber lösen.
- Offline-PWA für Scanner braucht Idempotenz-Disziplin im Backend.

### Folgeentscheidungen
- ADR (offen) Design-System-Strategie (eigenes Theme vs. später
  externes Library-Audit)
- ADR (offen) Native App ja/nein, wenn PWA für reale Scanner-Hardware
  Limitierungen zeigt

## Offene Punkte

- [ ] Test auf realen Fastlog-Handscanner-Modellen (Zebra, Honeywell)
- [ ] Festlegung i18n-Sprachen über Deutsch hinaus
- [ ] WCAG-2.2-AA-Audit-Plan
