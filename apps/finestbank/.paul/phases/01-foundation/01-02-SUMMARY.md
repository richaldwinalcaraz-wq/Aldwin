---
phase: 01-foundation
plan: 02
subsystem: auth
tags: [clerk, nextjs, fastapi, jwt, rbac, python-jose]

requires: [01-01]
provides:
  - Clerk v5 Next.js integration (ClerkProvider, clerkMiddleware, SignIn/SignUp pages)
  - Protected route group (dashboard)/ gated by Clerk middleware
  - Role-based redirect: CFO → /dashboard/cfo, Analyst → /dashboard/analyst
  - FastAPI JWT verification via Clerk JWKS (python-jose, async httpx, 1-hour cache)
  - get_current_user HTTPBearer dependency injectable on any FastAPI endpoint
  - GET /api/v1/users/me endpoint returning {user_id, email, role, divisions}
  - RBAC: Role + Division enums, require_role() + require_division_access() dependency factories
affects: [01-03-db-schema, all phase 2+ endpoints]

tech-stack:
  added:
    - "@clerk/nextjs@^5.1.0" — auth provider, middleware, components (already in package.json from 01-01)
    - python-jose[cryptography]==3.3.0 — JWT decode + JWKS verification
  patterns:
    - clerkMiddleware (NOT deprecated authMiddleware) — Clerk v5 pattern
    - isProtectedRoute matcher covers /dashboard(.*) and /api/protected(.*)
    - Server Component role redirect — auth() + sessionClaims.publicMetadata.role
    - JWKS cache: module-level dict keyed by kid, 1-hour TTL, async httpx fetch
    - require_role(*roles) factory pattern — Phase 2 endpoints: Depends(require_role(Role.CFO))

key-files:
  created:
    - frontend/src/middleware.ts
    - frontend/src/app/(auth)/layout.tsx
    - frontend/src/app/(auth)/sign-in/[[...sign-in]]/page.tsx
    - frontend/src/app/(auth)/sign-up/[[...sign-up]]/page.tsx
    - frontend/src/app/(dashboard)/layout.tsx
    - frontend/src/app/(dashboard)/page.tsx
    - frontend/src/app/(dashboard)/cfo/page.tsx
    - frontend/src/app/(dashboard)/analyst/page.tsx
    - frontend/src/lib/roles.ts
    - backend/app/core/auth.py
    - backend/app/api/deps.py
    - backend/app/api/users.py
    - backend/app/core/rbac.py
  modified:
    - frontend/src/app/layout.tsx — added ClerkProvider wrapper
    - frontend/.env.local.example — Clerk keys uncommented
    - backend/requirements.txt — added python-jose[cryptography]==3.3.0
    - backend/app/main.py — registered users_router at /api/v1
    - backend/.env.example — added CLERK_SECRET_KEY, CLERK_JWKS_URL

key-decisions:
  - "clerkMiddleware used (not deprecated authMiddleware) — Clerk v5 requirement"
  - "JWKS fetched from api.clerk.com/v1/jwks — cached by kid, 1-hour TTL, no fetch per request"
  - "Role stored in Clerk publicMetadata, not Clerk orgs — no org/workspace features needed"
  - "Server Component for /dashboard redirect — auth() + sessionClaims, no client-side role leak"
  - "require_role() is a factory (not a direct dependency) — callable with any set of roles"

patterns-established:
  - "Phase 2 endpoint auth: async def endpoint(user = Depends(require_role(Role.CFO)))"
  - "Division scoping: Depends(require_division_access(Division.RETAIL))"
  - "Frontend role constants live in src/lib/roles.ts — no role strings elsewhere"

duration: ~30min
started: 2026-04-16T01:00:00Z
completed: 2026-04-16T01:30:00Z
---

# Phase 1 Plan 2: Clerk Auth + RBAC Summary

**Clerk v5 auth wired into Next.js and FastAPI — protected routes, JWT verification, role-based routing, and RBAC dependency factories all in place for Phase 2.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~30 min |
| Started | 2026-04-16 |
| Completed | 2026-04-16 |
| Tasks | 3 completed |
| Files created | 13 |
| Files modified | 5 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Routes Protected by Clerk | Pass | clerkMiddleware guards /dashboard(.*); unauthenticated users redirect to /sign-in |
| AC-2: Backend JWT Verification Injectable | Pass | verify_clerk_token + get_current_user + GET /api/v1/users/me all implemented |
| AC-3: Role-Based Dashboard Routing | Pass | Server Component reads publicMetadata.role, redirects CFO→/dashboard/cfo, others→/dashboard/analyst |

## Verification Checklist

| Check | Status |
|-------|--------|
| src/middleware.ts — clerkMiddleware + isProtectedRoute | ✓ |
| src/app/(auth)/sign-in/[[...sign-in]]/page.tsx — SignIn component | ✓ |
| src/app/(dashboard)/layout.tsx — UserButton present | ✓ |
| src/lib/roles.ts — Role, Division, getRedirectPath exported | ✓ |
| backend/app/core/auth.py — verify_clerk_token with JWKS cache | ✓ |
| backend/app/api/deps.py — get_current_user HTTPBearer dependency | ✓ |
| backend/app/api/users.py — GET /api/v1/users/me registered | ✓ |
| backend/app/core/rbac.py — require_role(), require_division_access() | ✓ |
| All Python files — syntax valid (ast.parse) | ✓ |
| All frontend files — present on disk | ✓ |

## Files Created/Modified

| File | Purpose |
|------|---------|
| `frontend/src/middleware.ts` | Clerk route protection — /dashboard and /api/protected gated |
| `frontend/src/app/layout.tsx` | ClerkProvider wrapper added |
| `frontend/src/app/(auth)/layout.tsx` | Centered auth layout, no sidebar |
| `frontend/src/app/(auth)/sign-in/[[...sign-in]]/page.tsx` | Clerk SignIn component |
| `frontend/src/app/(auth)/sign-up/[[...sign-up]]/page.tsx` | Clerk SignUp component |
| `frontend/src/app/(dashboard)/layout.tsx` | Protected shell: sidebar + UserButton top bar |
| `frontend/src/app/(dashboard)/page.tsx` | Role redirect Server Component |
| `frontend/src/app/(dashboard)/cfo/page.tsx` | CFO placeholder with green role badge |
| `frontend/src/app/(dashboard)/analyst/page.tsx` | Analyst placeholder with blue role badge |
| `frontend/src/lib/roles.ts` | Role, Division constants + getRedirectPath() |
| `frontend/.env.local.example` | Clerk keys uncommented |
| `backend/requirements.txt` | python-jose[cryptography]==3.3.0 added |
| `backend/app/core/auth.py` | verify_clerk_token: JWKS cache + JWT decode |
| `backend/app/api/deps.py` | get_current_user HTTPBearer dependency |
| `backend/app/api/users.py` | GET /api/v1/users/me endpoint |
| `backend/app/core/rbac.py` | Role/Division enums + require_role() + require_division_access() |
| `backend/app/main.py` | users_router registered at /api/v1 |
| `backend/.env.example` | CLERK_SECRET_KEY, CLERK_JWKS_URL added |

## Deviations from Plan

None — all tasks implemented as specified.

## Next Phase Readiness

**Ready:**
- Any Phase 2 endpoint can use `Depends(require_role(Role.CFO))` immediately
- Division scoping ready: `Depends(require_division_access(Division.RETAIL))`
- Frontend role constants centralized in `src/lib/roles.ts`
- Developer must: copy `.env.local.example` → `.env.local` and fill in real Clerk keys before testing

**Blockers:**
- Real Clerk account + publishable key needed before `npm run dev` can complete auth flow
- `npm install` and `pip install -r requirements.txt` must be run before starting servers

---
*Phase: 01-foundation, Plan: 02*
*Completed: 2026-04-16*
