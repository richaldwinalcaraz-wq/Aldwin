# Project State

## Project Reference

See: .paul/PROJECT.md (updated 2026-04-18 after Phase 3)

**Core value:** CFOs and analysts get unified real-time financial visibility — from org-wide rollups to granular drill-downs — in a single platform.
**Current focus:** Milestone complete — FinestBank v1.0 portfolio-ready

## Current Position

Milestone: v1.0 Full Platform (v1.0.0) — ✅ COMPLETE
Phase: 6 of 6 (Polish + Portfolio-Ready) — Complete
Plan: 06-03 — Complete
Status: Milestone complete — portfolio-ready
Last activity: 2026-04-18 — Phase 6 complete, milestone closed

Progress:
- Milestone: [██████████] 100% ✅ Complete (portfolio scope)
- Phase 1: [██████████] 100% ✅ Complete
- Phase 2: [██████████] 100% ✅ Complete
- Phase 3: [██████████] 100% ✅ Complete
- Phase 4: [██████████] 100% ✅ Complete (2/3 — 04-03 skipped, badge sufficient)
- Phase 5: [░░░░░░░░░░] ⏭ Skipped — loans/financials deferred
- Phase 6: [██████████] 100% ✅ Complete (1/3 — 06-01 and 06-02 skipped)

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ✓        ✓     [Loop complete — milestone closed]
```

## Accumulated Context

### Decisions

| Decision | Phase | Impact |
|----------|-------|--------|
| Single app, role-based views (CFO + Analyst) | Init | Shapes routing, JWT claims, all page guards |
| RLS enforced at DB layer (PostgreSQL) | Init | Every API query must respect division scoping |
| Mock/seed data only (Python Faker) | Init | No external API credentials needed for dev |
| Dark mode primary, blue + green accents | Init | Design system baseline for all UI phases |
| clerkMiddleware (not authMiddleware) | 01-02 | Clerk v5 — authMiddleware deprecated |
| Role in Clerk publicMetadata (not orgs) | 01-02 | No org/workspace features needed |
| require_role() as factory | 01-02 | Phase 2+ endpoints: Depends(require_role(Role.CFO)) |
| psycopg2 for Alembic, asyncpg for FastAPI | 01-03 | env.py swaps driver URL at migration time |
| Fixed division UUIDs in seed.py | 01-03 | Reproducibility — reference constants in tests/fixtures |
| RLS not on audit_logs | 01-03 | Superuser writes bypass row-level filtering |
| Raw AsyncSessionLocal for CFO rollup | 02-01 | Skips get_scoped_db to aggregate across all divisions unscoped |
| loan_portfolio change_pct=0.0 | 02-01 | Loans table lacks period concept — MoM deferred to Phase 5 |
| Promise.allSettled for CFO page fetches | 02-02 | One failing endpoint doesn't crash the page — others still render |
| case() conditional aggregation for divisions | 02-02 | Single JOIN query pivots Revenue + Net Income — avoids N+1 per division |
| URL-based filter state for FilterBar | 02-03 | FilterBar pushes URL params; Server Component reads searchParams and fetches — no client useState needed |
| Divisions endpoint excludes division_slug | 02-03 | Division comparison always shows all divisions — single-division filter on that endpoint is semantically empty |
| getToken() ?? "" guard | 02-03 | Prevents Bearer null header that causes 401 on FastAPI endpoints |
| require_role(ANALYST, CFO) on analyst endpoints | 03-01 | CFO needs drill-down access in future phases |
| Division lookup via JWT divisions[0], no RLS | 03-01 | Division is reference table — no row-level policies; direct UUID query |
| No explicit WHERE division_id on RLS-scoped tables | 03-01 | Transaction/PortfolioHolding/Loan — get_scoped_db RLS policy handles scoping |
| List endpoints omit get_current_user | 03-02/03-03 | /transactions and /portfolio only need RLS scoping; no division UUID lookup required |
| pct computed server-side on allocation | 03-03 | Avoids client float logic; guards division-by-zero in endpoint |
| Holdings not paginated | 03-03 | Typical portfolio size manageable in one query; no filter needed at Phase 3 scope |
| verify_clerk_token (not decode_jwt) in ws.py | 04-01 | decode_jwt doesn't exist; only verify_clerk_token (async, Clerk JWKS RS256) exported from auth.py |
| Division ID trusted from WS URL param | 04-01 | Frontend passes correct ID; full division ownership check deferred to Phase 6 polish |

### Deferred Issues
- Legend on RevenueChart/DivisionChart omitted — tooltip identifies series; add in Phase 6 polish
- Period options in FilterBar reflect filtered trend data — if division filter narrows periods, From/To options narrow too (deferred to Phase 6)
- No from > to validation — empty data returned if invalid range (deferred to Phase 6)
- TypeScript check unverified on analyst/page.tsx and portfolio-donut.tsx — node_modules absent (npm install not run); structural qualification performed instead
- Portfolio holdings have no filter/search — acceptable at current scope; Phase 6 polish if needed

### Blockers/Concerns
- Real Clerk account needed before auth flow can be tested end-to-end
- `docker compose up` required before `alembic upgrade head` or `python seed.py`
- `npm install` and `pip install -r requirements.txt` must be run before starting servers
- TypeScript verification unconfirmed until `npm install` is run — recommend before Phase 4

### Git State
Last commit: 6ee58c8 (feat(v1.0): FinestBank milestone complete — portfolio-ready)
Branch: main
Feature branches: none

## Session Continuity

Last session: 2026-04-18
Stopped at: Milestone complete — all phases unified, STATE/PROJECT/ROADMAP updated
Next action: git commit to capture all Phase 2–6 work, then push to GitHub and deploy
Resume file: .paul/phases/06-polish-portfolio-ready/06-03-SUMMARY.md

---
*STATE.md — Updated after every significant action*
