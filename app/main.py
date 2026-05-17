from app.api.routes.auth_test import router as auth_router
from app.api.routes.orders_client import router as order_router
from app.api.routes.checkout import router as checkout_router
from app.api.routes.orders_artisan import router as artisan_router
from app.api.routes.carts import router as cart_router
from app.api.routes.webhook import router as webhook_router
from app.core.config import settings
from fastapi import FastAPI
import asyncio
import sys
from fastapi_pagination import add_pagination
from app.core.redis import lifespan

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(auth_router) # Remover quando conectar com a API de autenticação
app.include_router(cart_router)
app.include_router(checkout_router)
app.include_router(order_router)
app.include_router(artisan_router)
app.include_router(webhook_router)



add_pagination(app)