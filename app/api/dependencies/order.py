from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.database import get_session
from app.repositories.order_repository import OrderRepository
from app.repositories.shipping_repository import ShippingRepository
from app.services.cart_service import CartService
from app.api.dependencies.shipping import get_shipping_repository
from app.api.dependencies.cart import get_cart_service
from app.api.dependencies.integration import get_catalog_integration, get_accounts_integration, get_payment_integration
from app.integrations.catalog_integration import CatalogIntegration
from app.integrations.accounts_integration import AccountsIntegration
from app.integrations.payment_integration import PaymentIntegration

SessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_order_repository(session: SessionDep) -> OrderRepository:
    return OrderRepository(session=session)

def get_order_service(
    session: SessionDep,
    order_repo: OrderRepository = Depends(get_order_repository),
    shipping_repo: ShippingRepository = Depends(get_shipping_repository),
    cart_service: CartService = Depends(get_cart_service),
    catalog_inte: CatalogIntegration = Depends(get_catalog_integration),
    accounts_inte: AccountsIntegration = Depends(get_accounts_integration),
    payment_inte: PaymentIntegration = Depends(get_payment_integration)
) -> OrderService:
    return OrderService(
        session=session,
        order_repository=order_repo,
        shipping_repository=shipping_repo,
        cart_service=cart_service,
        catalog_integration=catalog_inte,
        accounts_integration=accounts_inte,
        payment_integration=payment_inte
    )