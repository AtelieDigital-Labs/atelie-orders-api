from fastapi import Depends
from app.api.dependencies.cart import get_cart_service
from app.services.shipping_service import ShippingService
from app.repositories.shipping_repository import ShippingRepository
from typing import Annotated
from redis.asyncio import Redis
from app.core.redis import get_redis
from app.api.dependencies.integration import get_catalog_integration, get_shipping_integration
from app.integrations.catalog_integration import CatalogIntegration
from app.integrations.shipping_integration import ShippingIntegration
from app.services.cart_service import CartService


RedisDep = Annotated[Redis, Depends(get_redis)]

def get_shipping_repository(redis: RedisDep) -> ShippingRepository:
    return ShippingRepository(redis=redis)


def get_shipping_service(
    shipping_repo: ShippingRepository = Depends(get_shipping_repository),
    cart_service: CartService = Depends(get_cart_service),
    catalog_inte: CatalogIntegration = Depends(get_catalog_integration),
    shipping_inte: ShippingIntegration = Depends(get_shipping_integration)
) -> ShippingService:
    return ShippingService(
        shipping_repository=shipping_repo, 
        cart_service=cart_service,
        catalog_integration=catalog_inte,
        shipping_integration=shipping_inte
    )