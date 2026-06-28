from ..constants import RoutingKey
from ..broker import broker
from ..events.order_created import OrderCreatedEvent
from ..exchanges import exchange_orders

async def publisher_order_created(data: OrderCreatedEvent):
    await broker.publish(
        exchange=exchange_orders,
        routing_key=RoutingKey.ORDER_CREATED_ROUTING_KEY,
        message=data
    )