---
phase: 03-analyst-view
plan: 03
subsystem: api, ui
tags: [fastapi, nextjs, recharts, portfolio, rls, donut-chart]

requires:
  - phase: 03-02
    provides: Transaction feed, paginated endpoint pattern, analyst page two-section scaffold

provides:
  - GET /api/v1/analyst/portfolio (holdings list + allocation breakdown, RLS-scoped)
  - PortfolioDonut client component (Recharts donut, dark theme, inline legend)
  - Analyst page third section (9-col holdings table + allocation chart, server-fetched)

affects: [phase-4-websockets, phase-6-polish]

tech-stack:
  added: []
  patterns:
    - Group-by aggregation with server-side pct computation (avoids client-side float logic)
    - Recharts donut pattern: PieChart + Pie innerRadius/outerRadius + Cell per slice + dark Tooltip
    - Three-column lg:grid-cols-3 layout (2/3 table + 1/3 chart)

key-files:
  created:
    - frontend/src/components/portfolio-donut.tsx
  modified:
    - backend/app/api/analyst.py
    - frontend/src/app/(dashboard)/analyst/page.tsx

key-decisions:
  - "get_current_user omitted from /portfolio — RLS via get_scoped_db handles scoping; consistent with /transactions pattern"
  - "pct computed server-side — clean separation; guards division-by-zero with conditional"
  - "Holdings not paginated — typical portfolio size manageable in single query; no URL-state filter needed"

patterns-established:
  - "List endpoint pattern (no division UUID lookup): require_role + get_scoped_db only"
  - "Donut chart: innerRadius=70 outerRadius=110 leaves center space; inline legend below chart"

duration: ~25min
started: 2026-04-18T00:00:00Z
completed: 2026-04-18T00:25:00Z
---

# Phase 3 Plan 03: Portfolio Holdings Summary

**Portfolio holdings table and allocation donut chart added to analyst page — `/api/v1/analyst/portfolio` endpoint returns RLS-scoped holdings ordered by market value with GROUP BY asset_type allocation breakdown; rendered as a 9-column table alongside a Recharts donut chart.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~25min |
| Started | 2026-04-18 |
| Completed | 2026-04-18 |
| Tasks | 2 completed |
| Files modified | 3 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Portfolio endpoint returns holdings and allocation | PASS | Returns `{holdings, allocation, total_market_value}`; holdings ordered by market_value DESC; allocation GROUP BY asset_type with server-side pct |
| AC-2: Viewer role rejected | PASS | `require_role(Role.ANALYST, Role.CFO)` blocks all other roles with 403 |
| AC-3: Holdings table renders 9 columns with P&L coloring | PASS (structural) | Asset, Type, Ticker, Qty, Unit Cost, Current Price, Market Value, P&L, Weight%; P&L green ≥0 / red <0; empty state message present |
| AC-4: Allocation donut chart renders by asset type | PASS (structural) | PieChart with innerRadius=70, Cell per slice, dark Tooltip, inline legend below; TypeScript check blocked by missing node_modules (documented blocker) |

## Accomplishments

- Added `GET /analyst/portfolio` endpoint — holdings list + GROUP BY asset_type allocation with server-side pct, RLS-scoped via get_scoped_db, no get_current_user needed
- Created `portfolio-donut.tsx` — Recharts PieChart donut with 7-color palette, dark-themed Tooltip, inline legend row, empty state
- Expanded `analyst/page.tsx` with third section: third fetch, 3 new interfaces (HoldingItem, AllocationSlice, PortfolioData), lg:grid-cols-3 layout (holdings table + donut chart)

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/app/api/analyst.py` | Modified | Appended `GET /portfolio` endpoint after `/transactions` |
| `frontend/src/components/portfolio-donut.tsx` | Created | Client component — Recharts donut chart with legend and empty state |
| `frontend/src/app/(dashboard)/analyst/page.tsx` | Modified | Added 3 interfaces, third fetch, portfolio section (table + donut) |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| `get_current_user` omitted from `/portfolio` | List endpoint needs only RLS scoping — no division UUID lookup required | Consistent with `/transactions` pattern from 03-02; cleaner dependency injection |
| `pct` computed server-side | Avoids floating-point logic in client; `round(..., 1) if total_mv else 0.0` guards division-by-zero | Clean separation between API and UI |
| Holdings not paginated | Typical portfolio size (10–50 positions) is manageable in one query; no filter state needed | Simpler than transaction feed; no URL-state required |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 0 | — |
| Scope additions | 0 | — |
| Deferred | 1 | TypeScript check blocked (pre-existing env issue) |

**Total impact:** No scope changes; one pre-existing blocker re-confirmed.

### Deferred Items

- TypeScript check (`npx tsc --noEmit`) unverifiable — `node_modules` absent (npm install not run). Same blocker as 03-01 and 03-02. Structural qualification performed: imports verified, prop types cross-checked, `"use client"` / no `"use client"` directives confirmed correct.

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| `node_modules` absent — TypeScript check unavailable | Structural qualification: verified all imports, type shapes, directive placement. No functional issue — environment setup blocker only. |

## Next Phase Readiness

**Ready:**
- Phase 3 complete — all three analyst views built (KPI summary, transaction feed, portfolio holdings)
- `get_scoped_db` RLS pattern confirmed for all three model types (Transaction, PortfolioHolding, Loan summary)
- Analyst page has stable three-section structure for Phase 4 to extend with real-time feeds
- Donut chart pattern established for any future allocation-style charts

**Concerns:**
- TypeScript verification remains unconfirmed until `npm install` is run; recommend running before Phase 4
- Portfolio holdings have no filter/search — acceptable at typical portfolio sizes; Phase 6 polish if needed

**Blockers:**
- None for Phase 4

---
*Phase: 03-analyst-view, Plan: 03*
*Completed: 2026-04-18*
