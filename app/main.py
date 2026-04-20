from fastapi import FastAPI
from core.config import settings

from api.routes.auth_test import router as auth_router
from api.routes.orders_client import router as order_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

app.include_router(auth_router) # Remover quando conectar com a API de autenticação
app.include_router(order_router)

