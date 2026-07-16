from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.database import get_session
from app.api.dependencies.order import get_order_repository
from app.api.dependencies.integration import get_catalog_integration, get_payment_integration
from app.integrations.payment_integration import PaymentIntegration
from app.integrations.catalog_integration import CatalogIntegration
from app.repositories.order_repository import OrderRepository
from app.services.webhook_service import WebhookService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_webhook_service(
    session: SessionDep,
    order_repo: OrderRepository = Depends(get_order_repository),
    payment_integration: PaymentIntegration = Depends(get_payment_integration),
    catalog_integration: CatalogIntegration = Depends(get_catalog_integration)
) -> WebhookService:
    return WebhookService(
        session=session, 
        order_repository=order_repo, 
        payment_integration=payment_integration, 
        catalog_integration=catalog_integration
    )