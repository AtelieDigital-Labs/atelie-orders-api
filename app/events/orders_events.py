import uuid
from sqlalchemy import event
from sqlalchemy.engine import Connection
from app.models.order import Order
from app.models.outbox import LogOutbox
from sqlalchemy.orm import Mapper
from datetime import datetime, timezone

@event.listens_for(Order, 'after_insert')
def generate_log_create_order(mapper: Mapper, connection: Connection, target: Order):
    log_payload = {
        "log_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "microservice": "Orders",
        "actor": {
            "user_id": "uuid_do_usuario_ou_artesao", # fazer processo do contextvars para pegar o id do usuário
            "role": "customer",
        },
        "action": "INSERT",
        "resource": "Order",
        "resource_id": target.order_id,
        "changes": {
            "status": {
            "old_value": None,
            "new_value": target.status if hasattr(target, 'status') else "CREATED"
            }
        },
        "reason": "Criação do pedido"
    }

    connection.execute(
        LogOutbox.__table__.insert().values(
            log_id = log_payload["log_id"],
            aggregate_type = "Order",
            aggregate_id = str(target.order_id), 
            payload = log_payload,
            processed = False
        )
    )
