from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.order import OrderStatus
from app.integrations.payment_integration import PaymentIntegration
from app.integrations.catalog_integration import CatalogIntegration
from app.repositories.order_repository import OrderRepository
from app.core.config import settings
import hmac
import hashlib
from fastapi import Request
from infra.messaging.publishers.order_paid import publisher_order_paid 
from infra.messaging.events.order_paid import OrderPaidEvent, OrderItemEvent


class WebhookService:

    MP_WEBHOOK_SECRET=settings.WEBHOOK_SECRET

    def __init__(
        self, 
        session: AsyncSession, 
        order_repository: OrderRepository, 
        payment_integration: PaymentIntegration,
        catalog_integration: CatalogIntegration,
    ):
        self.session = session
        self.order_repo = order_repository
        self.payment_inte = payment_integration
        self.catalog_inte = catalog_integration

    async def process_mercadopago_webhook(self, request: Request):

        print(f"URL Bruta: {request.url}")
        print(f"Header x-signature: {request.headers.get('x-signature')}")
        print(f"Query Param id: {request.query_params.get('id')}")
        print(f"Query Param data.id: {request.query_params.get('data.id')}")
        print(f"Tamanho do Secret em memória: {len(WebhookService.MP_WEBHOOK_SECRET)}")
        
        # Validação de segurança
        x_signature = request.headers.get("x-signature")
        x_request_id = request.headers.get("x-request-id")
        
        data_id_url = request.query_params.get("data.id") or request.query_params.get("id")

        if not x_signature or not data_id_url:
            return {"status": "ignorado", "reason": "Headers ou Query Params ausentes"}

        parts = x_signature.split(",")
        ts = None
        hash_v1 = None
        
        for part in parts:
            key_value = part.split("=", 1)
            if len(key_value) == 2:
                key = key_value[0].strip()
                val = key_value[1].strip()
                if key == "ts":
                    ts = val
                elif key == "v1":
                    hash_v1 = val

        if not ts or not hash_v1:
            return {"status": "erro", "reason": "Assinatura x-signature malformada (ts ou v1 ausentes)"}
    
        data_id_lower = str(data_id_url)

        manifest_parts = [f"id:{data_id_lower}"]

        if x_request_id:
            manifest_parts.append(f"request-id:{x_request_id}")
        
        manifest_parts.append(f"ts:{ts}")

        manifest = ";".join(manifest_parts) + ";"
        
        hmac_obj = hmac.new(
            WebhookService.MP_WEBHOOK_SECRET.encode('utf-8'), 
            msg=manifest.encode('utf-8'), 
            digestmod=hashlib.sha256
        )

        meu_hash = hmac_obj.hexdigest()

        if not hmac.compare_digest(meu_hash, hash_v1):
            print("\n--- DEBUG HMAC ---")
            print(f"Manifest gerado: {manifest}")
            print(f"Hash MP (v1): {hash_v1} | Meu Hash: {meu_hash}")
            print("------------------\n")
            print("Tentativa de fraude detectada: Assinatura HMAC inválida.")
            return {"status": "erro", "reason": "Assinatura HMAC inválida"}
        
        payload = await request.json()
        action = payload.get("action", "")

        # Busca do status
        if not action.startswith("order."):
            return {"status": "ignorado", "reason": f"Tópico {action} não é de order"}
        
        order_info = await self.payment_inte.get_merchant_order(data_id_url)

        if not order_info:
            return {"status": "error", "reason": "Ordem não encontrada no Mercado Pago"}

        status = order_info.get("status") 
        group_id_str = order_info.get("external_reference") 


        if status in ["processed", "paid", "closed"] and group_id_str:
            
            orders = await self.order_repo.get_order_group(group_id=group_id_str)
            
            if not orders:
                return {"status": "error", "reason": "Nenhum pedido local correspondente"}

            if orders[0].status == OrderStatus.PAID:
                return {"status": "successo", "reason": "Já processado"}
            
            events_to_publish = []

            for order in orders:
                order.status = OrderStatus.PAID
                order.transaction_id = str(data_id_url) 
                artisan_id = await self.catalog_inte.get_store_owner(order.store_id)

                event_items = [
                    OrderItemEvent(
                        product_variant_id=item.product_variant_id,
                        quantity=item.quantity
                    )
                    for item in order.items
                ]
                event = OrderPaidEvent(
                    order_id=str(order.order_id),
                    store_id=order.store_id,
                    artisan_id=artisan_id,
                    customer_id=order.user_id,
                    total_amount=order.artisan_ammount,
                    items=event_items,
                )

                events_to_publish.append(event)

            await self.session.commit()

            for event in events_to_publish:
                await publisher_order_paid(event)

            return {"status": "successo", "reason": "Pedidos atualizados e fundos distribuídos."}

        return {"status": "ignorado", "reason": f"Status da ordem: {status}"}

