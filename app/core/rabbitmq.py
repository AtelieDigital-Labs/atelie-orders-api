from infra.messaging.broker import broker
from infra.messaging.exchanges import declare_exchange
from contextlib import asynccontextmanager
from fastapi import FastAPI
from infra.messaging.queues import order_canceled_dlq
import asyncio
from infra.messaging.worker import process_outbox_messages

@asynccontextmanager
async def rabbit_lifespan(app: FastAPI):
    from infra.messaging.handlers.order_canceled import handler_order_canceled
    print("Conectando ao RabbitMQ e criando estruturas...")

    await broker.connect() 
    await broker.start()
    await declare_exchange(broker=broker)

    print("Iniciando o worker de polling do Outbox...")

    poller_task =asyncio.create_task(process_outbox_messages())

    try:
        yield  
        
    finally:
        print("Realizando encerramento para o worker do Outbox...")

        poller_task.cancel()
        try:
            await poller_task
        except asyncio.CancelledError:
            pass

        print("Desconectando do RabbitMQ...")
        await broker.stop()