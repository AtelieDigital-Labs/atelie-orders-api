import json

from .connection import get_connection
from .constants import ORDERS_EXCHANGE


class RabbitMQPublisher:
    def publish(self, queue: str, routing_key: str, message: dict):
        connection = get_connection()

        channel = connection.channel()

        channel.exchange_declare(
            exchange=ORDERS_EXCHANGE,
            exchange_type="topic",
            durable=True,
        )

        channel.queue_declare(
            queue=queue,
            durable=True,
        )

        channel.queue_bind(
            exchange=ORDERS_EXCHANGE,
            queue=queue,
            routing_key=routing_key,
        )

        channel.basic_publish(
            exchange=ORDERS_EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(message),
        )

        connection.close()