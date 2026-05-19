from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.order import OrderStatus
from app.integrations.payment_integration import PaymentIntegration
from app.integrations.catalog_integration import CatalogIntegration
from app.integrations.accounts_integration import AccountsIntegration
from app.repositories.order_repository import OrderRepository
from app.core.config import settings
import hmac
import hashlib
from fastapi import Request

class WebhookService:

    MP_WEBHOOK_SECRET=settings.WEBHOOK_SECRET

    @staticmethod
    async def process_mercadopago_webhook(request: Request, session: AsyncSession):
        # Validação de segurança
        x_signature = request.headers.get("x-signature")
        x_request_id = request.headers.get("x-request-id")
        
        data_id_url = request.query_params.get("data.id")

        if not x_signature or not x_request_id or not data_id_url:
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

        data_id_lower = data_id_url.lower()
        manifest = f"id:{data_id_lower};request-id:{x_request_id};ts:{ts};"
        
        hmac_obj = hmac.new(
            WebhookService.MP_WEBHOOK_SECRET.encode(), 
            msg=manifest.encode(), 
            digestmod=hashlib.sha256
        )

        meu_hash = hmac_obj.hexdigest()

        # print("\n--- DEBUG HMAC ---")
        # print(f"Secret Lida da Memória: '{WebhookService.MP_WEBHOOK_SECRET}'")
        # print(f"Manifest gerado: {manifest}")
        # print(f"Hash do Mercado Pago (v1): {hash_v1}")
        # print(f"Meu Hash Calculado: {meu_hash}")
        # print("------------------\n")
        
        if meu_hash != hash_v1:
            print("Tentativa de fraude detectada: Assinatura HMAC inválida.")
            #return {"status": "erro", "reason": "Assinatura HMAC inválida"}
        
        payload = await request.json()
        action = payload.get("action", "")

        # Busca do status
        if not action.startswith("order."):
            return {"status": "ignorado", "reason": f"Tópico {action} não é de order"}
        
        order_info = await PaymentIntegration.get_merchant_order(data_id_url)

        if not order_info:
            return {"status": "error", "reason": "Ordem não encontrada no Mercado Pago"}

        status = order_info.get("status") 
        group_id_str = order_info.get("external_reference") 


        if status in ["processed", "paid", "closed"] and group_id_str:
            
            orders = await OrderRepository.get_order_group(session=session, group_id=group_id_str)
            
            if not orders:
                return {"status": "error", "reason": "Nenhum pedido local correspondente"}

            if orders[0].status == OrderStatus.PAID:
                return {"status": "successo", "reason": "Já processado"}

            stock_payload = []

            for order in orders:
                order.status = OrderStatus.PAID
                order.transaction_id = str(data_id_url) 

                for item in order.items:
                    stock_payload.append({
                        "product_variant_id": item.product_variant_id,
                        "quantity": item.quantity
                    })

                try:
                    artisan_id = await CatalogIntegration.get_store_owner(order.store_id)
                    # PASSAR MÉTODO PARA MENSAGERIA
                    await AccountsIntegration.credit_wallet(
                        user_id=artisan_id,
                        amount=float(order.artisan_amount),
                        reference_order_id=str(order.order_id)
                    )
                except Exception as e:
                    print(f"Erro ao creditar artesão: {e}")

            # PASSAR MÉTODO PARA MENSSAGERIA
            if stock_payload:
                await CatalogIntegration.deacrese_stock(stock_payload)

            await session.commit()
            return {"status": "successo", "reason": "Pedidos atualizados e fundos distribuídos."}

        return {"status": "ignorado", "reason": f"Status da ordem: {status}"}

