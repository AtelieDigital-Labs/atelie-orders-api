from dataclasses import asdict
from ..broker import broker
from ..constants import RoutingKey
from ..exchanges import exchange_orders
from ..events.order_paid import OrderPaidEvent


async def publisher_order_paid(event: OrderPaidEvent):
    await broker.publish(
        exchange=exchange_orders,
        routing_key=RoutingKey.ORDER_PAID_ROUTING_KEY,
        message=asdict(event)
    )
