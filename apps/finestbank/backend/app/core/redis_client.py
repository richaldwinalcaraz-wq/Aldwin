import json

import redis.asyncio as aioredis
from fastapi import FastAPI


def channel_name(division_id: str) -> str:
    return f"transactions:{division_id}"


async def init_redis(app: FastAPI, redis_url: str) -> None:
    app.state.redis = aioredis.from_url(redis_url, decode_responses=True)


async def close_redis(app: FastAPI) -> None:
    await app.state.redis.aclose()


async def publish_transaction(redis: aioredis.Redis, division_id: str, payload: dict) -> None:
    await redis.publish(channel_name(division_id), json.dumps(payload))
