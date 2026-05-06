from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import OrderItem
from app.repositories.order_repository import OrderRepository
from app.services.cart_service import CartService
from fastapi import HTTPException
from app.integrations.accounts_integration import AccountsIntegration
from app.integrations.catalog_integration import CatalogIntegration
from app.schemas.order import OrderCheckoutRequest
from app.validators.validate import validate_address_user
from http import HTTPStatus




class OrderService: 
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
    async def create_new_order(order_data: OrderCheckoutRequest, session: AsyncSession, user_id: str):
        try:

            address_data = await AccountsIntegration.get_address(order_data.address_id)

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

            cart_items = await CartService.get_cart_items(session, user_id)

            if not cart_items:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Não existem items no carrinho do usuário para prosseguir com a compra.')
            
            products_ids = [item.product_variant_id for item in cart_items]

            catalog_data = await CatalogIntegration.fetch_all_prices(products_ids)

            items_store = {}
            for item in cart_items:
                variant_id = item.product_variant_id
                catalog_info = catalog_data.get(variant_id)

                if not catalog_info:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail=f'O produto {variant_id} não está mais disponível para venda'
                    )
                
                stock_available = catalog_info.get('stock', 0)
                if item.quantity > stock_available:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail=f'Estoque insuficiente para o produto {variant_id}'
                    )

                if item.store_id not in items_store:
                    items_store[item.store_id] = []
                items_store[item.store_id].append(item)
            
            orders_created = []

            for store_id, items_list in items_store.items():
                total_price = sum(
                    catalog_data[item.product_variant_id]['unit_price'] * item.quantity 
                    for item in items_list
                )

                store_shipping_cost = order_data.shipping_costs_per_store.get(store_id, 0.00)
                
                order_payload = {
                    "user_id": user_id,
                    "store_id": store_id,
                    "price": total_price,
                    "shipping_method": order_data.shipping_method,
                    "shipping_cost": store_shipping_cost,
                    "shipping_address": address_snapshot,
                    "payment_method": order_data.payment_method
                }
                
                new_order = await OrderRepository.create_order(
                    session=session,
                    order_data=order_payload
                )

                order_items_create = []

                for item in items_list:

                    unit_price = catalog_data[item.product_variant_id]['unit_price']

                    order_items_create.append(
                        OrderItem(
                            order_id=new_order.order_id,
                            product_variant_id=item.product_variant_id,
                            quantity=item.quantity,
                            unit_price=unit_price 
                        )
                    )

                await OrderRepository.create_order_items(session, order_items_create)
                orders_created.append(new_order.order_id)

            await CartService.clear_cart(session, user_id)

            await session.commit()

            stock_payload = [
                {
                    'product_variant_id': item.product_variant_id,
                    'quantity': item.quantity
                }
                for item in cart_items
            ]

            await CatalogIntegration.deacrese_stock(stock_payload)

            return {'message':'Pedido gerado', 'orders_id':orders_created}
        except Exception as e:
            await session.rollback()
            print(f'Erro ao gerar o pedido: {e}')
            raise e
