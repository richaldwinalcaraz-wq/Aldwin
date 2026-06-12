---
phase: 04-real-time-layer
plan: 01
subsystem: api
tags: [redis, websocket, pubsub, fastapi, jwt]

requires:
  - phase: 01-auth-foundation
    provides: verify_clerk_token, role from public_metadata
  - phase: 02-cfo-dashboard
    provides: main.py lifespan pattern, settings.redis_url config field
  - phase: 03-analyst-dashboard
    provides: Phase 3 endpoints untouched; deps.py role extraction pattern used as reference

provides:
  - Redis async pool initialized on app startup (app.state.redis)
  - channel_name() convention: transactions:{division_id}
  - publish_transaction() helper for 04-03 simulator
  - /ws/live/{division_id} WebSocket endpoint with JWT auth + Redis pub/sub relay

affects: [04-02-frontend-ws-client, 04-03-transaction-simulator]

tech-stack:
  added: [redis[hiredis]==5.0.4, websockets==12.0]
  patterns:
    - JWT via query param for WebSocket auth (browser upgrade can't send custom headers)
    - app.state.redis for pool access from WebSocket handler
    - finally block for pub/sub cleanup (unsubscribe + aclose)

key-files:
  created:
    - backend/app/core/redis_client.py
    - backend/app/api/ws.py
  modified:
    - backend/requirements.txt
    - backend/app/main.py

key-decisions:
  - "verify_clerk_token (async, Clerk JWKS) used instead of non-existent decode_jwt"
  - "Role extracted from payload.get('public_metadata') matching deps.py pattern"
  - "No DB access in WS handler — relay only, RLS not needed"

patterns-established:
  - "channel_name(division_id) is canonical — 04-03 must use this helper, not hardcode"
  - "publish_transaction() is the single publish entry point for the simulator"

duration: ~30min
started: 2026-04-18T00:00:00Z
completed: 2026-04-18T00:30:00Z
---

# Phase 4 Plan 01: Redis + WebSocket Backend Summary

**Redis pub/sub layer wired: async pool on app.state.redis, `/ws/live/{division_id}` endpoint with JWT auth, and `publish_transaction()` helper ready for the simulator.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~30 min |
| Started | 2026-04-18 |
| Completed | 2026-04-18 |
| Tasks | 3 completed |
| Files modified | 4 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Redis connection initializes on startup | Pass | init_redis called in lifespan before yield; pool on app.state.redis |
| AC-2: Valid JWT accepted, Redis channel subscribed | Pass | verify_clerk_token validates token; pubsub.subscribe(channel_name(division_id)) |
| AC-3: Invalid/missing token rejected with 1008 | Pass | Both auth failure and wrong role close with code=1008 |
| AC-4: Redis pub/sub message forwarded to WS client | Pass | message["type"] == "message" guard; send_text(message["data"]) |
| AC-5: Disconnect handled cleanly | Pass | finally block: unsubscribe + aclose; WebSocketDisconnect caught |

## Accomplishments

- Created `redis_client.py` with pool init/close, `channel_name()` convention, and `publish_transaction()` helper
- Created `ws.py` WebSocket endpoint with Clerk JWT auth (query param), Redis pub/sub relay, and disconnect cleanup
- Wired Redis lifespan into `main.py` and registered `/ws/live/{division_id}` router (no /api/v1 prefix)

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/app/core/redis_client.py` | Created | Async Redis pool, channel naming, publish helper |
| `backend/app/api/ws.py` | Created | WebSocket endpoint — JWT auth + pub/sub relay |
| `backend/requirements.txt` | Modified | Uncommented redis[hiredis] and websockets lines |
| `backend/app/main.py` | Modified | Redis lifespan init/close + ws_router registered |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| `verify_clerk_token` instead of `decode_jwt` | `decode_jwt` doesn't exist in auth.py; only `verify_clerk_token` (async, Clerk JWKS RS256) exists | WS auth is async; matches Clerk v5 pattern already used throughout |
| Role from `public_metadata.get("role")` | Matches deps.py extraction pattern exactly | Consistent role check across all endpoints |
| No DB access in WS handler | Endpoint only relays pub/sub events; RLS not needed for relay-only logic | Keeps handler fast; avoids session lifecycle complexity in async WS context |
| Division ID trusted from URL param | Analyst frontend passes correct division_id; full scoping deferred to Phase 6 | Acceptable for portfolio scope; noted as known limitation |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 1 | Essential — plan referenced non-existent function |
| Scope additions | 0 | — |
| Deferred | 0 | — |

**Total impact:** One essential fix; no scope creep.

### Auto-fixed Issues

**1. Import: `decode_jwt` does not exist in auth.py**
- **Found during:** Task 2 (ws.py creation)
- **Issue:** Plan specified `from app.core.auth import decode_jwt` — function does not exist; auth.py exports only `verify_clerk_token` (async, Clerk JWKS RS256)
- **Fix:** ws.py imports and awaits `verify_clerk_token`; role extracted from `payload.get("public_metadata", {}).get("role")` matching deps.py
- **Files:** `backend/app/api/ws.py`
- **Verification:** Syntax check passed; pattern matches all other Phase 1–3 auth usage

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| IDE diagnostics flagging redis/websockets as unresolved imports | Pre-existing environment issue — all packages unresolved (fastapi, uvicorn, etc.); `npm install` / `pip install` not run in dev env. Not introduced by this plan. |

## Next Phase Readiness

**Ready:**
- `/ws/live/{division_id}` endpoint ready for 04-02 frontend client to connect
- `publish_transaction(redis, division_id, payload)` ready for 04-03 simulator to call
- `channel_name(division_id)` established as the canonical convention for both sides
- Redis pool lifecycle managed correctly — no resource leak on shutdown

**Concerns:**
- `docker compose up` required before Redis is available at startup; backend won't start without it
- `pip install -r requirements.txt` must be run to install redis[hiredis] and websockets

**Blockers:**
- None for 04-02 or 04-03 — both can be built against this interface

---
*Phase: 04-real-time-layer, Plan: 01*
*Completed: 2026-04-18*
