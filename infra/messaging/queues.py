from faststream.rabbit import RabbitQueue
from .constants import RoutingKey, Queue

order_canceled_dlq = RabbitQueue(
    name=Queue.ORDER_EXPIRED_QUEUE,
    routing_key=RoutingKey.STOCK_RESERVATION_EXPIRE_ROUTING_KEY,
    durable=True
)