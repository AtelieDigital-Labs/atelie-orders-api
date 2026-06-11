import uuid
from sqlalchemy import event
from sqlalchemy.engine import Connection
from app.models.order import Order
from app.models.outbox import LogOutbox
from sqlalchemy.orm import Mapper
from datetime import datetime, timezone
from sqlalchemy.orm.attributes import get_history
from app.core.context import current_user_id
from app.core.logger import setup_trigger_logger


logger = setup_trigger_logger()

@event.listens_for(Order, 'after_insert')
def generate_log_create_order(mapper: Mapper, connection: Connection, target: Order):
    actor_id = str(current_user_id.get())

    log_payload = {
        "log_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "microservice": "Orders",
        "actor": {
            "user_id": actor_id
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

    logger.info(f"[INSERT] Gatilho acionado com sucesso para o recurso Order (ID: {target.order_id}). Log salvo na tabela Outbox.")

@event.listens_for(Order, 'before_update')
def generate_log_update_order(mapper: Mapper, connection: Connection, target: Order):

    status_history = get_history(target, 'status')

    if not status_history.has_changes():
        return
    
    old_status = status_history.deleted[0] if status_history.deleted else None

    new_status = status_history.added[0] if status_history.added else None

    old_value_str = old_status.value if hasattr(old_status, 'value') else str(old_status)
    new_value_str = new_status.value if hasattr(new_status, 'value') else str(new_status)

    actor_id = current_user_id.get()

    if not actor_id:
        actor_id = "mercadopago_webhook"
        reason = "Atualização automática via Webhook de Pagamento"
    else:
        actor_id = str(actor_id)
        reason = "Atualização manual pelo artesão"

    log_payload = {
        "log_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "microservice": "Orders",
        "actor": {
            "user_id": actor_id
        },
        "action": "UPDATE",
        "resource": "Order",
        "resource_id": target.order_id,
        "changes": {
            "status": {
            "old_value": old_value_str,
            "new_value": new_value_str
            }
        },
        "reason": reason
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

    logger.info(
        f" [UPDATE] Gatilho acionado com sucesso. Status alterado de {old_value_str} para {new_value_str} no pedido {target.order_id}."
    )
