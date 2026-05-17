from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.order import OrderStatus
from app.integrations.payment_integration import PaymentIntegration
from app.integrations.catalog_integration import CatalogIntegration
from app.integrations.accounts_integration import AccountsIntegration
from app.repositories.order_repository import OrderRepository

class WebhookService:
    @staticmethod
    async def process_mercadopago_webhook(payload: dict, session: AsyncSession):
        # 1. O Mercado Pago envia a ação e o ID do objeto dentro de 'data' ou 'resource'
        action = payload.get("action") or payload.get("topic")
        
        # Só processamos se for uma atualização de pagamento
        if action not in ["order.created", "order.updated", "order"]:
            return {"status": "ignorado", "reason": "Nenhum evento de pagamento"}

        # Extrai o ID do pagamento (a estrutura do JSON pode variar levemente na API v1)
        payment_id = payload.get("data", {}).get("id")
        if not payment_id:
            payment_id = payload.get("resource", "").split("/")[-1] # Tenta extrair da URL
            
        if not payment_id:
            return {"status": "ignorado", "reason": "Nenhum pagamento com essa identificação encontrado"}

        # 2. Faz a requisição reversa (Segurança contra fraudes)
        payment_info = await PaymentIntegration.verify_payment(payment_id)
        if not payment_info:
            return {"status": "error", "reason": "Pagamento não encontrado no Mercado Pago"}

        status = payment_info.get("status")

        group_id_str = payment_info.get("external_reference") 

        # ALTERAR PARA APPROVED DEPOIS, USO ASSIM PORQUE NÃO FOI PAGO
        if status == "pending" and group_id_str:
            
            # Busca todas as ordens vinculadas a esse pagamento
            orders = await OrderRepository.get_order_group(session=session, group_id = group_id_str)
            

            if not orders:
                return {"status": "error", "reason": "Não foi encontrado nenhum pedido com essa identificação"}

            # Verificação de Idempotência: Se a primeira já estiver PAGA, ignoramos o webhook repetido
            if orders[0].status == OrderStatus.PAID:
                return {"status": "successo", "reason": "Processado"}

            stock_payload = []

            # 3. Itera sobre cada loja do carrinho
            for order in orders:
                # Atualiza o status
                order.status = OrderStatus.PAID
                order.transaction_id = str(payment_id) # Salva o ID do Mercado Pago para rastreio

                # Prepara os itens para baixar o estoque do Catalog
                for item in order.items:
                    stock_payload.append({
                        "product_variant_id": item.product_variant_id,
                        "quantity": item.quantity
                    })

                # 4. Acha o dono da loja e credita a carteira
                try:
                    artisan_id = await CatalogIntegration.get_store_owner(order.store_id)
                    
                    # Dispara o crédito no DRF - Mensageria
                    await AccountsIntegration.credit_wallet(
                        user_id=artisan_id,
                        amount=float(order.artisan_amount),
                        reference_order_id=str(order.order_id)
                    )
                except Exception as e:
                    print(f"Erro Crítico ao repassar valor para o artesão da loja {order.store_id}: {e}")

            # 5. Efetiva a baixa no estoque em lote 
            if stock_payload:
                await CatalogIntegration.deacrese_stock(stock_payload)

            # Salva tudo no banco do Orders
            await session.commit()

            return {"status": "successo", "reason": "Pedidos atualizados e fundos distribuídos."}

        return {"status": "ignorado", "reason": f"Status do pagamento: {status}"}