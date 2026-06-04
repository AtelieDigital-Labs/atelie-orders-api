from fastapi import Depends
from app.repositories.cart_repository import CartRepository
from app.integrations.catalog_integration import CatalogIntegration
from app.services.cart_service import CartService
from typing import Annotated
from redis.asyncio import Redis
from app.core.redis import get_redis
from app.api.dependencies.integration import get_catalog_integration

RedisDep = Annotated[Redis, Depends(get_redis)]

def get_cart_repository(redis: RedisDep) -> CartRepository:
    return CartRepository(redis=redis)

def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    catalog_inte: CatalogIntegration = Depends(get_catalog_integration)
) -> CartService:
    return CartService(cart_repository=cart_repo, catalog_integration=catalog_inte)