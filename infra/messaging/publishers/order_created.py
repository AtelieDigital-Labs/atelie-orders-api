from infra.messaging.constants import RoutingKey
from infra.messaging.broker import broker
from infra.messaging.events.order_created import OrderCreatedEvent
from infra.messaging.exchanges import exchange_orders

async def publisher_order_created(data: OrderCreatedEvent):
    await broker.publish(
        exchange=exchange_orders,
        routing_key=RoutingKey.ORDER_CREATED_ROUTING_KEY,
        message=data
    )