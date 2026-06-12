---
phase: 02-cfo-dashboard
plan: 03
subsystem: ui, api
tags: [fastapi, nextjs, server-components, url-state, query-params, sqlalchemy]

requires:
  - phase: 02-02
    provides: rollup.py with trends+divisions endpoints, RevenueChart, DivisionChart, CFO page base with Promise.allSettled

provides:
  - Optional filter params (division_slug, from_period, to_period) on /rollup/kpis and /rollup/trends
  - Optional period params (from_period, to_period) on /rollup/divisions
  - FilterBar "use client" component — division switcher + period range selects — URL-param-driven
  - CFO page accepts searchParams prop, passes filters to all 3 API calls, renders FilterBar

affects: [phase-3-analyst, phase-6-polish]

tech-stack:
  added: []
  patterns:
    - URL-based filter state via useRouter+useSearchParams — no client useState needed in server components
    - buildQuery inline helper for constructing optional query strings from param objects
    - Server component reads searchParams, passes to fetch; client component only pushes URL changes

key-files:
  created:
    - frontend/src/components/filter-bar.tsx
  modified:
    - backend/app/api/rollup.py
    - frontend/src/app/(dashboard)/cfo/page.tsx

key-decisions:
  - "URL-based filter state (not React state) — FilterBar pushes params, Next.js re-renders Server Component"
  - "Divisions endpoint receives only period params, not division_slug — always shows all divisions for comparison"
  - "trendPoints.map(t => t.period) used for period options — filtered view's periods as range reference (Phase 2 acceptable)"

patterns-established:
  - "Filter state lives in URL — client component pushes, server component reads and fetches"
  - "buildQuery: Record<string, string|undefined> → '?k=v' | '' — reusable inline pattern"
  - "division_id resolved once at endpoint entry, reused across all _sum_statement calls (no N+1)"

duration: ~1 session
started: 2026-04-18T00:00:00Z
completed: 2026-04-18T00:00:00Z
---

# Phase 2 Plan 03: Division Switcher + Date Range Picker Summary

**CFO dashboard made interactive — optional division and period filters wired end-to-end from URL search params through backend SQLAlchemy queries.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~1 session |
| Tasks | 3 completed |
| Files modified | 3 (1 created, 2 modified) |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Rollup endpoints accept optional filters | Pass | kpis+trends accept division_slug+from_period+to_period; divisions accepts period params only; org-wide behavior unchanged when params absent |
| AC-2: FilterBar renders and updates URL | Pass | 3 selects (division, from, to) with router.push on change; controlled via props; "use client" |
| AC-3: CFO page responds to searchParams | Pass | buildQuery appends params to all 3 fetches; divisions fetch excludes division_slug; FilterBar rendered between header and KpiGrid |

## Accomplishments

- Backend filter params added without changing any response shapes — org-wide behavior fully preserved when params absent
- `_sum_statement` helper extended with optional `division_id` kwarg — single lookup, reused across all calls
- FilterBar uses URL as single source of truth — no useState needed in the Server Component page

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/app/api/rollup.py` | Modified | Optional Query params on all 3 endpoints; _sum_statement division_id kwarg; loan query division filter |
| `frontend/src/components/filter-bar.tsx` | Created | "use client" — 3 selects push URL params on change via router.push |
| `frontend/src/app/(dashboard)/cfo/page.tsx` | Modified | searchParams prop, buildQuery helper, FilterBar import+render, getToken ?? "" guard |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| URL-based filter state | FilterBar is "use client" but CFO page is a Server Component — URL is the only shared state channel | Clean App Router pattern; no prop drilling or global state; browser back button works |
| Divisions endpoint excludes division_slug | Showing one division's bar chart vs. others requires all divisions in frame; single-division filter on divisions endpoint is semantically empty | Correct scoping — divisions always shows comparison |
| trendPoints periods for FilterBar options | Avoids a 4th unfiltered fetch; filtered view's available periods are reasonable as range reference | Minor limitation: when division filter is active, fewer periods shown as options (acceptable for Phase 2) |

## Deviations from Plan

None — plan executed exactly as specified.

## Issues Encountered

None.

## Next Phase Readiness

**Ready:**
- All 3 rollup endpoints stable and filterable — kpis, trends, divisions all behind require_role(CFO)
- FilterBar component pattern established — props-only, URL-driven, no internal state
- CFO page fully interactive — division + period filters narrow all KPIs and charts in sync

**Concerns:**
- Period options in FilterBar reflect filtered trend data — if division filter reduces periods shown, From/To options narrow too. Full period list would require an unfiltered trends fetch (deferred to Phase 6 polish)
- No from/to validation — selecting from > to will return empty data (deferred to Phase 6 polish per plan boundaries)

**Blockers:** None

---
*Phase: 02-cfo-dashboard, Plan: 03*
*Completed: 2026-04-18*
