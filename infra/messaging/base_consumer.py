import json

from .connection import get_connection

class RabbitMQConsumer:
    def consume(self, exchange: str, queue: str, routing_key: str, callback):
        connection = get_connection()

        channel = connection.channel()

        channel.exchange_declare(
            exchange=exchange,
            exchange_type="topic",
            durable=True,
        )

        channel.queue_declare(
            queue=queue,
            durable=True,
        )

        channel.queue_bind(
            exchange=exchange,
            queue=queue,
            routing_key=routing_key,
        )

        def wrapper(ch, method, properties, body):
            data = json.loads(body)

            try:
                callback(data)

                ch.basic_ack(
                    delivery_tag=method.delivery_tag
                )

            except Exception as e:
                print(e)

                ch.basic_nack(
                    delivery_tag=method.delivery_tag,
                    requeue=False,
                )

        channel.basic_consume(
            queue=queue,
            on_message_callback=wrapper,
        )

        print(f"Listening queue: {queue}")

        channel.start_consuming()