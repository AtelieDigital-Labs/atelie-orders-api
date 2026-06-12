from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import redis.asyncio as redis
from app.core.config import settings
from redis.asyncio import Redis


REDIS_URL = settings.REDIS_URL

@asynccontextmanager
async def redis_lifespan(app: FastAPI):
    pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
    redis_client = redis.Redis.from_pool(pool)
    
    app.state.redis = redis_client
    
    yield 
    
    await redis_client.close()
    await pool.disconnect()


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
