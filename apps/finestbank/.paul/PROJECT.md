# FinestBank

## What This Is

FinestBank is a real-time financial intelligence dashboard that serves two audiences in one product: CFOs who need org-wide KPI rollups across all business divisions, and fintech analysts who need deep drill-down access into transactions, portfolios, loans, and financial statements. Built as a single app with division-based sub-accounts, role-based views, and live data feeds across all core financial domains.

## Core Value

CFOs and fintech analysts get unified real-time financial visibility — from org-wide rollups to granular division-level drill-downs — in a single platform without switching tools.

## Current State

| Attribute | Value |
|-----------|-------|
| Type | Application |
| Version | 1.0.0 |
| Status | Complete — Portfolio-Ready |
| Last Updated | 2026-04-18 |

## Requirements

### Core Features

- CFO org-wide rollup dashboard across all business divisions
- Analyst division drill-down (transactions, portfolio, loans, financials)
- Real-time transaction feed via WebSockets
- Role-based access control (CFO / Analyst / Viewer)
- Multi-division sub-account model (Retail, Corporate, Treasury, Wealth Management)

### Validated (Shipped)
- ✓ Role-based access control (CFO / Analyst / Viewer) — Phase 1
- ✓ Multi-division sub-account model (Retail, Corporate, Treasury, Wealth Management) — Phase 1
- ✓ Individual transactions stored with TimescaleDB hypertable — Phase 1
- ✓ RLS at DB layer (division-scoped policies on 4 tables) — Phase 1
- ✓ CFO org-wide rollup dashboard (KPI cards, trend charts, division comparison, interactive filters) — Phase 2
- ✓ Analyst division drill-down (transactions, portfolio holdings, allocation chart) — Phase 3
- ✓ Real-time transaction feed via WebSockets + Redis pub/sub (LiveFeed component with status badge) — Phase 4
- ✓ Portfolio-ready: README, Mermaid architecture diagram, Dockerfile, Vercel + Railway deploy configs — Phase 6

### Active (In Progress)
_None — milestone complete_

### Planned (Next)
_None — milestone complete_

### Out of Scope
- Real banking API integrations (Plaid, Stripe, core banking) — mock data only for portfolio
- Mobile app — desktop/tablet responsive only
- Loans + Financials module (Phase 5) — deferred; badge-level demo sufficient for portfolio
- Audit log viewer + CSV/PDF export (Phase 6 plans 01–02) — deferred; not needed for portfolio demo

## Target Users

**Primary: CFO / Executive**
- Needs org-wide financial KPIs at a glance
- Views all divisions rolled up
- Minimal clicks, maximum clarity

**Secondary: Fintech Analyst**
- Scoped to assigned division(s)
- Needs full drill-down: transactions, portfolio, loans, P&L
- High data density preferred

**Tertiary: Viewer**
- Read-only access to assigned division(s)
- Reports and snapshots

## Context

**Business Context:**
Portfolio project demonstrating enterprise-grade financial dashboard architecture. Target audience: potential employers and clients evaluating full-stack + data visualization skills.

**Technical Context:**
Greenfield build. No existing systems to integrate. Mock/seed data via Python Faker. Real-time simulation via background task generating transactions.

## Constraints

### Technical Constraints
- PostgreSQL + TimescaleDB required for time-series financial data
- WebSocket support needed for real-time transaction feed
- Row-level security must be enforced at DB layer (not just frontend)
- Clerk handles auth — JWT 15-min expiry + refresh token rotation

### Business Constraints
- Portfolio project — must be demo-able with a live URL
- No real PII — all mock data
- Must include README, screenshots, architecture diagram for portfolio presentation

### Compliance Constraints
- Audit logging required (who viewed/exported what, when) — signals compliance awareness to reviewers

## Key Decisions

| Decision | Rationale | Date | Status |
|----------|-----------|------|--------|
| Single app with role-based views | CFO and Analyst share one codebase; role claims in JWT control rendering | 2026-04-16 | Active |
| Division = business unit | Sub-accounts represent internal divisions, not external clients | 2026-04-16 | Active |
| Individual transactions stored | Every debit/credit stored; aggregations computed at query time via TimescaleDB | 2026-04-16 | Active |
| RLS at DB layer | Analysts cannot query outside their division even with direct DB access | 2026-04-16 | Active |
| Mock data first | Python Faker seed script; no real banking API dependencies | 2026-04-16 | Active |
| Dark mode primary | Finance dashboard convention; blue + green accent for trust + growth | 2026-04-16 | Active |
| CFO rollup server-side | Aggregated at /api/rollup, not client-side joins | 2026-04-16 | Active |
| clerkMiddleware (not authMiddleware) | Clerk v5 — authMiddleware deprecated | 2026-04-16 | Active |
| Role in Clerk publicMetadata (not orgs) | No org/workspace features needed | 2026-04-16 | Active |
| require_role() as factory | Phase 2+ endpoints: Depends(require_role(Role.CFO)) | 2026-04-16 | Active |
| psycopg2 for Alembic, asyncpg for FastAPI | Alembic doesn't support async; env.py swaps driver in URL | 2026-04-16 | Active |
| Fixed division UUIDs in seed.py | Reproducibility — test fixtures reference same IDs every run | 2026-04-16 | Active |
| RLS not applied to audit_logs | Superuser writes must bypass row-level filtering | 2026-04-16 | Active |
| Raw AsyncSessionLocal for CFO rollup | Skips get_scoped_db to aggregate across all divisions unscoped | 2026-04-18 | Active |
| Promise.allSettled for CFO page fetches | One failing endpoint doesn't crash the page — others still render | 2026-04-18 | Active |
| case() conditional aggregation for divisions | Single JOIN query pivots Revenue + Net Income — avoids N+1 per division | 2026-04-18 | Active |
| URL-based filter state for FilterBar | FilterBar pushes URL params; Server Component reads searchParams and fetches — no client useState needed | 2026-04-18 | Active |
| Divisions endpoint excludes division_slug | Division comparison always shows all divisions — single-division filter on that endpoint is semantically empty | 2026-04-18 | Active |
| List endpoints omit get_current_user | /transactions and /portfolio only need RLS scoping (get_scoped_db) — no division UUID lookup required | 2026-04-18 | Active |
| pct computed server-side on allocation | Avoids client float logic; guards division-by-zero in endpoint | 2026-04-18 | Active |
| Holdings not paginated | Typical portfolio size manageable in one query; no URL-state filter needed at Phase 3 scope | 2026-04-18 | Active |

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| All 5 financial domains functional | 100% | 3/5 (transactions, portfolio, real-time) | Scoped — loans/financials deferred |
| Real-time feed stable under load | WebSocket stable | LiveFeed badge + status indicator | Phase 4 ✅ |
| CFO rollup correctness | Aggregates across all divisions | ✓ with optional division/period filters | Phase 2 ✅ |
| RBAC enforced | No analyst reaches CFO rollup | ✓ Clerk JWT + RLS enforced | Phases 1–3 ✅ |
| Portfolio ready | README + architecture diagram + deploy configs | ✓ README, Dockerfile, vercel.json | Phase 6 ✅ |

## Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | Next.js 14 + Tailwind CSS + shadcn/ui | Fast builds, great dashboard primitives |
| Charts | Recharts | Line/bar/area/donut — finance-appropriate |
| Backend | FastAPI (Python) | Financial data processing, ML-extensible |
| Real-time | WebSockets + Redis Pub/Sub | Live transaction stream |
| Database | PostgreSQL + TimescaleDB | Time-series optimized |
| Auth | Clerk | RBAC + org/sub-account management |
| Hosting | Vercel (frontend) + Railway (backend + DB) | Zero-config deploys |
| Seed Data | Python Faker | Realistic mock financial data |
| Migrations | Alembic | FastAPI DB migration tool |

## Links

| Resource | URL |
|----------|-----|
| Repository | TBD |
| Production | TBD — Vercel deployment |
| Planning | projects/finestbank/PLANNING.md |

---
*PROJECT.md — Updated when requirements or context change*
*Last updated: 2026-04-18 after Phase 6 — milestone complete*
