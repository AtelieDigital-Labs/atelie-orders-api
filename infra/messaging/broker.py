from faststream.rabbit import RabbitBroker
from faststream import FastStream
from app.core.config import settings

broker = RabbitBroker(settings.MESSAGING_URL)
app = FastStream(broker)