from contextlib import asynccontextmanager
from fastapi import FastAPI
import redis.asyncio as redis
from redis.asyncio import Redis
from app.core.config import settings

REDIS_URL = settings.REDIS_URL

redis_client: Redis | None = None


@asynccontextmanager
async def redis_lifespan(app: FastAPI):
    global redis_client

    pool = redis.ConnectionPool.from_url(
        REDIS_URL,
        decode_responses=True,
    )

    redis_client = redis.Redis.from_pool(pool)

    yield

    await redis_client.close()
    await pool.disconnect()


def get_redis() -> Redis:
    assert redis_client is not None
    return redis_client