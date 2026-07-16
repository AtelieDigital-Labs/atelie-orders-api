from .redis import redis_lifespan
from .rabbitmq import rabbit_lifespan
from contextlib import AsyncExitStack, asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(redis_lifespan(app))
        await stack.enter_async_context(rabbit_lifespan(app))

        yield