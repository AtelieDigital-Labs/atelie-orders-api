from infra.messaging.broker import broker
from infra.messaging.exchanges import declare_exchange
from contextlib import asynccontextmanager
from fastapi import FastAPI
from infra.messaging.queues import order_canceled_dlq

@asynccontextmanager
async def rabbit_lifespan(app: FastAPI):
    from infra.messaging.handlers.order_canceled import handler_order_canceled
    print("Conectando ao RabbitMQ e criando estruturas...")
    await broker.connect() 
    await broker.start()
    await declare_exchange(broker=broker)
    try:
        yield  # Aqui a API fica rodando e aceitando requisições HTTP
    finally:
        print("Desconectando do RabbitMQ...")
        await broker.stop()