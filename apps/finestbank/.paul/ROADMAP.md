# Roadmap: FinestBank

## Overview

FinestBank ships in six phases: foundation (auth, schema, seed data), CFO dashboard, analyst drill-down views, real-time WebSocket layer, loans and financials modules, and a final polish pass to make the project portfolio-ready with a live demo URL, screenshots, and documentation.

## Current Milestone

**v1.0 — Full Platform** (v1.0.0)
Status: ✅ Complete
Phases: 6 of 6 (Phases 5 and partial 4/6 scoped out — portfolio demo)

## Phases

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 1 | Foundation | 3 | ✅ Complete | 2026-04-16 |
| 2 | CFO Dashboard | 3 | ✅ Complete | 2026-04-18 |
| 3 | Analyst View | 3 | ✅ Complete | 2026-04-18 |
| 4 | Real-Time Layer | 2/3 | ✅ Complete | 2026-04-18 |
| 5 | Loans + Financials | 0/3 | ⏭ Skipped | — |
| 6 | Polish + Portfolio-Ready | 1/3 | ✅ Complete | 2026-04-18 |

## Phase Details

### Phase 1: Foundation

**Goal:** Working auth, DB schema, seed data, and base API — the platform's skeleton
**Depends on:** Nothing (first phase)
**Research:** Likely (Clerk + TimescaleDB setup, Alembic migrations)

**Scope:**
- Next.js + FastAPI project scaffold
- Clerk auth integration (login, roles, division scoping)
- PostgreSQL + TimescaleDB schema + Alembic migrations
- Python Faker seed script (all divisions, all financial domains)
- Base API with division-scoped RLS middleware

**Plans:**
- [x] 01-01: Project scaffold (Next.js + FastAPI + Docker DB)
- [x] 01-02: Clerk auth + RBAC + division scoping
- [x] 01-03: DB schema + migrations + seed data

---

### Phase 2: CFO Dashboard

**Goal:** CFO can log in and see a live org-wide financial summary
**Depends on:** Phase 1 (auth, DB, seed data)
**Research:** Unlikely (internal patterns)

**Scope:**
- Org-wide rollup API (`/api/rollup`)
- CFO landing page: KPI cards + trend charts
- Division comparison chart
- Division switcher (top bar)
- Date range picker wired to all queries

**Plans:**
- [x] 02-01: Rollup API + KPI cards
- [x] 02-02: Trend charts + division comparison
- [x] 02-03: Division switcher + date range picker

---

### Phase 3: Analyst View

**Goal:** Analyst can log in, see their division's transactions and portfolio
**Depends on:** Phase 2 (role-based routing established)
**Research:** Unlikely (internal patterns)

**Scope:**
- Division drill-down pages
- Transaction feed (paginated, filterable by type/category/date/amount)
- Portfolio holdings table + allocation donut chart
- Role-based routing (CFO → overview, Analyst → their division)

**Plans:**
- [x] 03-01: Division drill-down page + role routing
- [x] 03-02: Transaction feed (paginated + filterable)
- [x] 03-03: Portfolio holdings + allocation chart

---

### Phase 4: Real-Time Layer

**Goal:** Transaction feed updates in real time without page refresh
**Depends on:** Phase 3 (transaction feed exists)
**Status:** ✅ Complete (2 of 3 plans — 04-03 simulator skipped, badge sufficient)

**Plans:**
- [x] 04-01: Redis + WebSocket backend
- [x] 04-02: Frontend WebSocket client + live feed UI
- [~] 04-03: Transaction simulator — skipped (LiveFeed status badge sufficient for portfolio demo)

---

### Phase 5: Loans + Financials

**Goal:** All 5 financial domains fully functional
**Status:** ⏭ Skipped — portfolio scope reduced; transactions + portfolio sufficient for demo

**Plans:**
- [~] 05-01: Loan book module — skipped
- [~] 05-02: Financial statements (P&L + Balance Sheet) — skipped
- [~] 05-03: Cash flow + period selector — skipped

---

### Phase 6: Polish + Portfolio-Ready

**Goal:** Demo-able, documented — portfolio ready
**Status:** ✅ Complete (1 of 3 plans — 06-01 and 06-02 skipped, 06-03 delivered essentials)

**Plans:**
- [~] 06-01: Audit log viewer + export (CSV/PDF) — skipped
- [~] 06-02: Responsive + loading/empty/error states — skipped
- [x] 06-03: README, architecture diagram, Dockerfile, Vercel + Railway configs

---
*Roadmap created: 2026-04-16*
*Last updated: 2026-04-18 — Milestone v1.0 complete (portfolio scope)*
