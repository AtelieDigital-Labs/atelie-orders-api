from fastapi import FastAPI
from core.config import settings

from api.routes.orders_client import order_client_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

app.include_router(order_client_router)

