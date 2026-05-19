from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import OrderItem, OrderStatus
from app.repositories.order_repository import OrderRepository
from app.services.cart_service import CartService
from fastapi import HTTPException, Depends
from app.integrations.accounts_integration import AccountsIntegration
from app.integrations.catalog_integration import CatalogIntegration
from app.schemas.order import OrderCheckoutRequest, OrderArtisanStatusUpdate
from app.validators.validate import validate_address_user
from http import HTTPStatus
import uuid
from redis.asyncio import Redis
from decimal import Decimal
from app.integrations.payment_integration import PaymentIntegration
from app.repositories.shipping_repository import ShippingRepository

VALID_TRANSITIONS = {
    OrderStatus.PAID: [OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.CANCELLED],
    OrderStatus.REFUSED: [],
    OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
    OrderStatus.SHIPPED: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: []
}


class OrderService: 
    @staticmethod
    async def update_status_order(session: AsyncSession, order_id: int, token: str, update_status: OrderArtisanStatusUpdate):
        store_id = await CatalogIntegration.get_store_id(token)

        order = await OrderRepository.get_order_artisan(session, order_id, str(store_id))

        if not order:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Pedido não encontrado ou não pertence a este artesão')

        status = update_status.status

        if status not in VALID_TRANSITIONS.get(order.status, []):
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Não é possível trocar o status atual para {update_status.status.label}' )
        
        order.status = status

        if status == OrderStatus.SHIPPED and update_status.tracking_code:
            order.tracking_code = update_status.tracking_code
        
        order_updated = await OrderRepository.update_status_order(session, order)

        return order_updated
        

    @staticmethod
    async def get_order_artisan_by_id(session: AsyncSession, order_id: int, token: str):
        store_id = await CatalogIntegration.get_store_id(token)

        order = await OrderRepository.get_order_artisan(session, order_id, str(store_id))

        if not order:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pedido não encontrado ou não pertence a este artesão")
        
        return order

    @staticmethod
    async def get_all_orders_artisan(session: AsyncSession, token: str):
        store_id = await CatalogIntegration.get_store_id(token)

        return await OrderRepository.get_all_orders_artisan(session, str(store_id))


    @staticmethod
    async def get_order_by_id(session: AsyncSession, order_id: int, user_id: str):
        order = await OrderRepository.get_order(session, order_id, user_id)

        if not order:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pedido não encontrado ou não pertence a este usuário")

        return order
    
    @staticmethod
    async def get_all_orders(session: AsyncSession, user_id: str):
        return await OrderRepository.get_all_orders(session, user_id)


    @staticmethod
    async def create_new_order(order_data: OrderCheckoutRequest, session: AsyncSession, redis: Redis, user_id: str, token: str):
        try:
            
            group_id = uuid.uuid4()
            total_cart_amount = Decimal("0.00")
            fee_percentage = Decimal("0.05")

            client_data = await AccountsIntegration.get_data_user(token=token)

            address_data = await AccountsIntegration.get_address(address_id=order_data.address_id, token=token)

            validate_address_user(address_data, user_id)

            address_snapshot = {
                "street" : address_data.get('street'),
                "number" : address_data.get('number'),
                "complement" : address_data.get('complement', ''),
                "neighborhood" : address_data.get('neighborhood'),
                "city" : address_data.get('city'),
                'state': address_data.get('state'),
                'zip_code': address_data.get('zip_code')
            } 

            saved_quotes = await ShippingRepository.get_freight(redis=redis, user_id=user_id)

            if not saved_quotes:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cotação de frete expirada ou não encontrada. Retorne a página anterior e selecione o frete novamente.")
            
            if order_data.shipping_method == "Econômico":
                shipping_costs_per_store = saved_quotes["cheapest"]["stores_breakdown"] 
            elif order_data.shipping_method == "Expresso":
                shipping_costs_per_store = saved_quotes["fastest"]["stores_breakdown"]
            else:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Método de frete inválido.")


            cart_data = await CartService.get_items(redis=redis, user_id=user_id)

            if not cart_data["items"]:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Não existem items no carrinho do usuário para prosseguir com a compra.')
            
            
            products_ids = [item["product_variant_id"] for item in cart_data["items"]]

            catalog_data = await CatalogIntegration.fetch_all_prices(products_ids)

            items_store = {}
            for item in cart_data["items"]:
                variant_id = item["product_variant_id"]
                catalog_info = catalog_data.get(variant_id)

                if not catalog_info:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail=f'O produto {variant_id} não está mais disponível para venda'
                    )
                
                # Precisa corrigir o risco de concorrência que isso traz, pois dois usuários podem estar tentando comprar o mesmo produto ao mesmo tempo
                stock_available = catalog_info.get('stock', 0)
                if item["quantity"] > stock_available:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail=f'Estoque insuficiente para o produto {variant_id}'
                    )
                
                store_id = item["store_id"]
                if store_id not in items_store:
                    items_store[store_id] = []
                items_store[store_id].append(item)
            
            for store_id, items_list in items_store.items():
                products_price = Decimal("0.00")

                
                for item in items_list:
                    variant_id = item["product_variant_id"]
                    unit_price = Decimal(str(catalog_data[variant_id]['unit_price']))
                    quantity = Decimal(str(item["quantity"]))
                    products_price += (unit_price * quantity)

                store_shipping_cost = Decimal(str(shipping_costs_per_store.get(store_id, 0.00)))
                # Taxa do Ateliê Digital por pedido
                store_fee = products_price * fee_percentage
                # Valor do artesão 
                artisan_ammount = Decimal(str((products_price - store_fee) + store_shipping_cost))
                total_cart_amount += (products_price + store_shipping_cost)
                
                order_payload = {
                    "user_id": user_id,
                    "store_id": store_id,
                    "price": products_price,
                    "checkout_group_id": group_id,
                    "shipping_method": order_data.shipping_method,
                    "shipping_cost": store_shipping_cost,
                    "shipping_address": address_snapshot,
                    "payment_method": order_data.payment_method,
                    "platform_fee": store_fee,
                    "artisan_ammount": artisan_ammount
                }
                
                new_order = await OrderRepository.create_order(
                    session=session,
                    order_data=order_payload
                )

                order_items_create = []

                for item in items_list:
                    variant_id = item["product_variant_id"]
                    unit_price = Decimal(str(catalog_data[variant_id]['unit_price']))

                    order_items_create.append(
                        OrderItem(
                            order_id=new_order.order_id,
                            product_variant_id=variant_id,
                            quantity=item["quantity"],
                            unit_price=unit_price 
                        )
                    )

                await OrderRepository.create_order_items(session=session, items_data=order_items_create)
            
            await session.commit()

            try: 
                await ShippingRepository.delete_freight(redis=redis, user_id=user_id)
                await CartService.clear_cart(redis=redis, user_id=user_id)

            except Exception as e:
                print(f"Falha ao limpar carrinho do usuário. Erro {e}")

        except HTTPException:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            print(f"ERRO REAL CAPTURADO: {e}")
            raise HTTPException(
                status_code=HTTPStatus.BAD_GATEWAY, 
                detail="Ocorreu um erro interno ao processar seu pedido."
            )

        try:
            payment_payload = {
                "total_amount": str(float(total_cart_amount)),
                "payment_method": order_data.payment_method.lower(),
                "checkout_group_id": str(group_id),
                "buyer_email": client_data['email'],
                "buyer_first_name": client_data['first_name'],
                "buyer_last_name": client_data['last_name'],
            }

            mp_response = await PaymentIntegration.generate_payment(payload=payment_payload)

            if not mp_response:
                raise Exception("Falha ao gerar pagamento na api de pagamento")
            
            try:
                mercadopago_id = mp_response['id']
                payment_data = mp_response['transactions']['payments'][0]['payment_method']
                pix = payment_data['qr_code_base64']
                pix_copia_cola = payment_data['qr_code']
            except (KeyError, IndexError) as e:
                raise Exception(f"Estrutura do PIX não encontrada no retorno do MP. Erro: {e}. Retorno: {mp_response}")

        except Exception as e:
            print(f"🚨 ERRO REAL CAPTURADO: {e}")
            raise HTTPException(
                status_code=HTTPStatus.BAD_GATEWAY, 
                detail="Pedido criado! Porém, ocorreu um erro ao gerar o pagamento. Acesses Meus Pedidos para tentar pagar novamente."
            )

        return {
            'message':'Pedido gerado', 
            'checkout_group_id':str(group_id),
            'payment_info': {
                'id': mercadopago_id,
                'qr_code_base64': pix,
                'qr_code': pix_copia_cola
            }
        }