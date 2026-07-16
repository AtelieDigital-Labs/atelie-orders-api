from fast_depends import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.cart import get_cart_service
from app.api.dependencies.integration import get_accounts_integration, get_catalog_integration, get_payment_integration
from app.api.dependencies.shipping import get_shipping_repository
from app.core.database import get_session
from app.core.redis import get_redis
from app.integrations.accounts_integration import AccountsIntegration
from app.integrations.catalog_integration import CatalogIntegration
from app.integrations.payment_integration import PaymentIntegration
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.shipping_repository import ShippingRepository
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from ..broker import broker
from ..queues import order_canceled_dlq
from ..exchanges import exchange_dlq
from ..events.stock_reserved import StockReservedExpiredEvent
from app.api.dependencies.order import get_order_repository

@broker.subscriber(
    exchange=exchange_dlq,
    queue=order_canceled_dlq
)
async def handler_order_canceled(
        data: StockReservedExpiredEvent, 
        session: AsyncSession = Depends(get_session),
        redis = Depends(get_redis),
        payment_inte = Depends(get_payment_integration)
    ):
    order_repo= OrderRepository(session=session)
    shipping_repo = ShippingRepository(redis=redis)
    cart_repo = CartRepository(redis)
    catalog_inte = CatalogIntegration()
    accounts_inte = AccountsIntegration()
    cart_service = CartService(cart_repository=cart_repo, catalog_integration=catalog_inte)

    service = OrderService(
        session=session,
        order_repository=order_repo,
        shipping_repository=shipping_repo,
        cart_service=cart_service,
        catalog_integration=catalog_inte,
        accounts_integration=accounts_inte,
        payment_integration=payment_inte
    )
    return await service.expired(data.order_id)