from app.api.routes.auth_test import router as auth_router
from app.api.routes.orders_client import router as order_router
from app.core.config import settings
from fastapi import FastAPI

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

app.include_router(auth_router) # Remover quando conectar com a API de autenticação
app.include_router(order_router)

