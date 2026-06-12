# FinestBank — Financial Intelligence Dashboard
<!-- Type: application | Status: Ideation Complete -->

## Metadata
| Field | Value |
|---|---|
| **Project Name** | FinestBank |
| **Type** | Application |
| **Purpose** | Portfolio project |
| **Status** | Ideation complete — ready for `/seed launch` |
| **Directory** | `projects/finestbank/` |

---

## Problem Statement

Finance executives and analysts lack a unified platform that provides both high-level strategic visibility and granular analytical depth in real time. CFOs need org-wide KPI rollups across all business divisions without switching tools. Analysts need to drill into transactions, portfolios, loans, and financial statements scoped to their division.

**FinestBank** solves this with a single-app financial intelligence platform: one login, multi-division sub-accounts, role-based views, and real-time data feeds across all core financial domains.

---

## Target Users

| Role | Access | Primary Need |
|---|---|---|
| **CFO** | All divisions (rolled up) | Org-wide KPIs, trends, forecasts at a glance |
| **Analyst** | Assigned division(s) | Deep drill-down: transactions, portfolio, loans, P&L |
| **Viewer** | Assigned division(s), read-only | Reports, snapshots, exports |

---

## Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| **Frontend** | Next.js 14 + Tailwind CSS + shadcn/ui + Recharts | Fast builds, great dashboard primitives, clean finance UI |
| **Backend** | FastAPI (Python) | Financial data processing, easy ML/forecasting extension later |
| **Real-time** | WebSockets via FastAPI + Redis Pub/Sub | Lightweight live data simulation |
| **Database** | PostgreSQL + TimescaleDB | Purpose-built for time-series financial data |
| **Auth** | Clerk | Best-in-class sub-account/org management + RBAC |
| **Hosting** | Vercel (frontend) + Railway (backend + DB) | Zero-config deploys, scales cleanly |
| **Seed Data** | Python Faker | Realistic mock transactions, portfolios, loans, financials |

---

## Data Model

```
Organization (FinestBank tenant)
  └── Division (business unit: Retail, Corporate, Treasury, etc.)
        ├── Transactions       — individual debit/credit records, timestamped
        ├── Portfolio          — assets, allocations, daily valuations
        ├── LoanBook           — individual loans, repayment schedules, status
        └── FinancialStatement — P&L, balance sheet, cash flow (period snapshots)

Users
  └── Role: CFO | Analyst | Viewer
  └── Scoped to: Organization (CFO) or specific Division(s) (Analyst/Viewer)
```

### Key Tables

```sql
-- Divisions
divisions (id, org_id, name, code, created_at)

-- Transactions
transactions (id, division_id, type, amount, currency, description,
              counterparty, category, timestamp, balance_after)

-- Portfolio Holdings
portfolio_holdings (id, division_id, asset_name, asset_type, quantity,
                    unit_price, total_value, allocation_pct, date)

-- Loan Book
loans (id, division_id, borrower_name, principal, outstanding_balance,
       interest_rate, start_date, maturity_date, status, repayment_schedule)

-- Financial Statements
financial_statements (id, division_id, period, period_type,
                      revenue, expenses, net_income,
                      total_assets, total_liabilities, equity,
                      operating_cashflow, investing_cashflow, financing_cashflow)

-- Audit Log
audit_logs (id, user_id, action, resource_type, resource_id, metadata, timestamp)
```

---

## API Surface

### REST Endpoints

```
GET  /api/divisions                         — list all divisions (CFO only)
GET  /api/divisions/{id}/summary            — KPI rollup for a division
GET  /api/transactions?division&range&page  — paginated transaction feed
POST /api/transactions/filter               — advanced filter + search
GET  /api/portfolio/{division_id}           — holdings + performance metrics
GET  /api/loans/{division_id}               — loan book + health metrics
GET  /api/financials/{division_id}          — P&L, balance sheet, cash flow
GET  /api/rollup                            — CFO org-wide aggregation
GET  /api/audit?user&resource&range         — audit log (admin only)
```

### WebSocket

```
WS   /ws/live/{division_id}  — real-time transaction stream via Redis pub/sub
```

### Auth (Clerk)
- JWT with 15-minute expiry + refresh tokens
- All routes protected by division-scoped middleware
- Role claims embedded in JWT payload

---

## Security Considerations

| Concern | Implementation |
|---|---|
| **Data isolation** | Row-level security (RLS) enforced at PostgreSQL — analysts cannot query outside their division even with direct DB access |
| **Authentication** | Clerk JWT, 15-min expiry, refresh token rotation |
| **Authorization** | Role-based middleware on every API route |
| **Audit logging** | Every view/export/filter action logged with user, resource, timestamp |
| **Sensitive data** | No real PII — all mock data with Faker-generated names and account numbers |
| **HTTPS** | Enforced on all endpoints (Vercel + Railway handle TLS) |

---

## UI/UX Design

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  Top Bar: Division Switcher | Date Range | Live ● | User │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ Sidebar  │           Main Content Area                  │
│          │                                              │
│ Overview │   KPI Cards → Charts → Data Tables           │
│ Txn Feed │                                              │
│ Portfolio│                                              │
│ Loans    │                                              │
│ Financials│                                             │
│ Settings │                                              │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

### Visual Direction
- **Theme:** Dark mode primary
- **Accent:** Electric blue (`#3B82F6`) + Emerald green (`#10B981`)
- **Charts:** Recharts for KPI lines/bars, area charts for time-series, donut for allocations
- **Transaction feed:** Real-time ticker feel with live WebSocket updates
- **Data density:** High — TradingView-inspired, clean grid, minimal chrome

### Key Views

**CFO Overview (default landing)**
- Org-wide KPI cards: Total Revenue, Net Income, Cash Position, Loan Book Value, Portfolio Value
- Revenue vs Expenses trend (all divisions, 30/90/180 day)
- Division performance comparison
- Live transaction activity indicator

**Analyst — Division Drill-Down**
- Division KPI summary
- Transaction feed (real-time, filterable by type/category/date/amount)
- Portfolio breakdown (holdings table + allocation chart)
- Loan book (health status, upcoming maturities, default rate)
- Financial statements (P&L, balance sheet, cash flow tabs)

---

## Deployment Strategy

| Environment | Frontend | Backend | Database |
|---|---|---|---|
| **Development** | `localhost:3000` | `localhost:8000` | Local PostgreSQL + TimescaleDB (Docker) |
| **Production** | Vercel | Railway | Railway PostgreSQL + TimescaleDB |

### CI/CD
- GitHub repo with `main` → auto-deploy to Vercel + Railway
- Environment variables managed via Vercel/Railway dashboards
- DB migrations via Alembic (FastAPI)

---

## Integration Points

| Integration | Purpose |
|---|---|
| **Clerk** | Auth, org/sub-account management, user roles |
| **Redis** | WebSocket pub/sub for real-time transaction streaming |
| **TimescaleDB** | Time-series optimized queries on transactions + portfolio history |
| **Python Faker** | Seed script to generate realistic financial data per division |

---

## Phase Breakdown

### Phase 1 — Foundation
- Project scaffold: Next.js + FastAPI + PostgreSQL
- Clerk auth integration (login, roles, division scoping)
- DB schema creation + Alembic migrations
- Seed data script (divisions, transactions, portfolio, loans, financials)
- Basic API with division-scoped middleware

**Deliverable:** Login works, divisions exist, seed data populates, API returns data

---

### Phase 2 — CFO Dashboard
- Org-wide rollup API (`/api/rollup`)
- CFO landing page: KPI cards + trend charts
- Division comparison chart
- Division switcher in top bar
- Date range picker wired to all queries

**Deliverable:** CFO can log in and see live org-wide financial summary

---

### Phase 3 — Analyst View
- Division drill-down pages
- Transaction feed (paginated, filterable)
- Portfolio holdings table + allocation donut chart
- Role-based routing (CFO → overview, Analyst → their division)

**Deliverable:** Analyst can log in, see their division's transactions and portfolio

---

### Phase 4 — Real-Time Layer
- Redis pub/sub setup on Railway
- FastAPI WebSocket endpoint (`/ws/live/{division_id}`)
- Frontend WebSocket client with live transaction feed
- Seed data simulator (background task generating mock transactions)

**Deliverable:** Transaction feed updates in real time without page refresh

---

### Phase 5 — Loans + Financials Module
- Loan book page: table, health indicators, maturity timeline
- Financial statements page: P&L, Balance Sheet, Cash Flow tabs
- Period selector (monthly, quarterly, annual)
- Charts for each statement type

**Deliverable:** All 5 financial domains fully functional

---

### Phase 6 — Polish + Portfolio-Ready
- Audit log viewer (admin)
- Export to CSV / PDF (transactions, statements)
- Responsive layout (tablet + desktop)
- Loading states, empty states, error boundaries
- README with setup instructions, architecture diagram, screenshots

**Deliverable:** Portfolio-ready — demo-able, documented, visually polished

---

## Skill Loadout

| Skill | Use |
|---|---|
| `ui-ux-pro-max` | Dashboard layout, component hierarchy, dark theme system |
| `ui-styling` | Tailwind + shadcn component styling, finance color system |
| `design-system` | KPI card, chart, table component library |
| `paul` | Managed phase-by-phase build execution |

---

## Quality Gates

- [ ] Auth + RLS working before any data is exposed
- [ ] Seed data covers all divisions and all financial domains
- [ ] WebSocket connection stable under simulated load
- [ ] CFO rollup aggregates correctly across all divisions
- [ ] All routes enforce role-based access (no analyst can reach CFO rollup)
- [ ] Portfolio project standard: README, screenshots, live demo URL

---

**Graduated:** 2026-04-16
**Location:** `apps/finestbank/`
**README:** `apps/finestbank/README.md`
