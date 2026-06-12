from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

import redis.asyncio as aioredis

from app.core.auth import verify_clerk_token
from app.core.redis_client import channel_name

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/live/{division_id}")
async def live_feed(
    websocket: WebSocket,
    division_id: str,
    token: str = Query(...),
):
    # Validate JWT before accepting the connection
    try:
        payload = await verify_clerk_token(token)
        public_metadata = payload.get("public_metadata") or {}
        role = public_metadata.get("role", "viewer")
        if role not in ("cfo", "analyst"):
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    redis: aioredis.Redis = websocket.app.state.redis
    channel = channel_name(division_id)
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():
            if websocket.client_state != WebSocketState.CONNECTED:
                break
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
