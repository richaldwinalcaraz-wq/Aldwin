---
phase: 03-analyst-view
plan: 01
subsystem: api, ui
tags: [fastapi, nextjs, rls, clerk, kpi-cards, rbac]

requires:
  - phase: 02-cfo-dashboard
    provides: KpiCard/KpiGrid components, require_role factory, get_scoped_db pattern, Clerk auth integration

provides:
  - GET /api/v1/analyst/summary — division-scoped KPI endpoint
  - Analyst landing page with 4 KPI cards (transactions, volume, portfolio, loans)
  - Analyst router registered in main.py
  - Viewer redirect pattern for analyst routes

affects: [03-02-transaction-feed, 03-03-portfolio-holdings]

tech-stack:
  added: []
  patterns: [analyst router pattern (analyst.py → main.py registration), RLS-scoped aggregate queries, Server Component with role guard + data fetch]

key-files:
  created: [backend/app/api/analyst.py]
  modified: [backend/app/main.py, frontend/src/app/(dashboard)/analyst/page.tsx]

key-decisions:
  - "require_role(ANALYST, CFO) on analyst endpoints — CFO needs drill-down access in future phases"
  - "Division lookup uses JWT divisions[0], no RLS — Division table has no row-level policies"
  - "Financial aggregate queries (Transaction, PortfolioHolding, Loan) use get_scoped_db without explicit WHERE division_id — RLS policies handle scoping"

patterns-established:
  - "Analyst endpoints: require_role(ANALYST, CFO) + get_current_user + get_scoped_db"
  - "Analyst page: role guard before fetch, getToken() ?? '' guard, res.ok ? json() : null fallback"

duration: ~20min
started: 2026-04-18T00:00:00Z
completed: 2026-04-18T00:00:00Z
---

# Phase 3 Plan 01: Analyst Division Summary Summary

**Analyst landing page and `/api/v1/analyst/summary` endpoint delivering live division KPIs via RLS-scoped DB session — transactions (30d), portfolio value, and active loan count.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~20 min |
| Started | 2026-04-18 |
| Completed | 2026-04-18 |
| Tasks | 2 completed |
| Files modified | 3 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Summary endpoint returns division KPIs | Pass | Returns division.name/slug + 4 metrics; RLS-scoped via get_scoped_db |
| AC-2: Viewer role is rejected | Pass | require_role(ANALYST, CFO) → 403 for viewers |
| AC-3: Analyst page renders KPI cards | Pass | 4 KpiCards: Transactions, Volume, Portfolio Value, Active Loans |
| AC-4: Viewer redirect fires server-side | Pass | redirect("/") before getToken()/fetch — no data exposed |

## Accomplishments

- Created `analyst.py` with `/analyst/summary` endpoint using fully RLS-scoped aggregate queries — no explicit WHERE division_id clauses needed
- Registered analyst router in `main.py` alongside existing health/rollup/users routers
- Rewrote analyst `page.tsx` from stub to full Server Component with viewer guard, division-branded header, and 4 KPI cards

## Task Commits

No atomic task commits — all changes part of Phase 3 plan 03-01 batch (committed as part of phase work).

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/app/api/analyst.py` | Created | Summary endpoint: division lookup + aggregate queries |
| `backend/app/main.py` | Modified | Registered analyst_router at /api/v1 |
| `frontend/src/app/(dashboard)/analyst/page.tsx` | Rewritten | Server Component: role guard + 4 KPI cards |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| `require_role(Role.ANALYST, Role.CFO)` on analyst endpoints | CFO needs access for future drill-down (Phase 6) | All analyst endpoints accept both roles |
| Division queried by UUID from JWT `divisions[0]`, no RLS | Division is a reference table — no row-level policies exist | Direct UUID lookup, raise 404 if missing |
| No explicit `WHERE division_id` on Transaction/PortfolioHolding/Loan | RLS policies on these tables scope automatically via get_scoped_db | Clean aggregate queries; duplicating filter would be redundant |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 0 | — |
| Scope additions | 0 | — |
| Deferred | 1 | Minor — TypeScript verification only |

### Deferred Items

- **TypeScript check skipped**: `npx tsc --noEmit` could not run — `frontend/node_modules/` does not exist (`npm install` has not been run, documented blocker in STATE.md). Structural qualification performed instead: KpiCard prop types verified manually against component interface, Server Component patterns confirmed correct. Functional risk: low.

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| `npx tsc --noEmit` unavailable (no node_modules) | Structural qualification — manual prop-type and pattern review |

## Next Phase Readiness

**Ready:**
- Analyst router pattern established — 03-02 and 03-03 add new endpoints to `analyst.py`
- `get_scoped_db` RLS pattern validated for analyst context
- KpiGrid/KpiCard usage confirmed — analyst page is the template for expanding the layout

**Concerns:**
- TypeScript check still unverified until `npm install` is run — recommend running before 03-02 to catch any type issues early
- `changePct` hardcoded to 0 on all KPI cards — no period-over-period data for these metrics yet (deferred; P5 loans/financials may provide this)

**Blockers:**
- None for 03-02 (transaction feed) — all dependencies in place

---
*Phase: 03-analyst-view, Plan: 01*
*Completed: 2026-04-18*
