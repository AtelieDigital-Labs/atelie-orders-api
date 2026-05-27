from dataclasses import asdict
from infra.messaging.base_publisher import RabbitMQPublisher
from infra.messaging.constants import ORDER_PAID_QUEUE, ORDER_PAID_ROUTING_KEY
from ..events.order_paid import OrderPaidEvent

def publisher_order_paid(event: OrderPaidEvent):
    publisher = RabbitMQPublisher()

    publisher.publish(
        queue=ORDER_PAID_QUEUE,
        routing_key=ORDER_PAID_ROUTING_KEY,
        message = asdict(event)
    )