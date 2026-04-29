from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import OrderItem
from app.repositories.order_repository import OrderRepository
from app.services.cart_service import CartService
from fastapi import HTTPException
from app.integrations.catalog_integration import CatalogIntegration


class OrderService: 
    @staticmethod
    async def create_new_order(session: AsyncSession, user_id: str):
        try:

            #implementar busca do endereço 

            cart_items = await CartService.get_cart_items(session, user_id)

            if not cart_items:
                raise HTTPException(status_code=400, detail='Não existem items no carrinho do usuário para prosseguir com a compra.')
            
            products_ids = [item.product_variant_id for item in cart_items]

            catalog_data = await CatalogIntegration.fetch_all_prices(products_ids)

            items_store = {}
            for item in cart_items:
                variant_id = item.product_variant_id
                catalog_info = catalog_data.get(variant_id)

                if not catalog_info:
                    raise HTTPException(
                        status_code=400,
                        detail=f'O produto {variant_id} não está mais disponível para venda'
                    )
                
                stock_available = catalog_info.get('stock', 0)
                if item.quantity > stock_available:
                    raise HTTPException(
                        status_code=400,
                        detail=f'Estoque insuficiente para o produto {variant_id}'
                    )

                if item.store_id not in items_store:
                    items_store[item.store_id] = []
                items_store[item.store_id].append(item)
            
            orders_created = []

            for store_id, items_list in items_store.items():
                # Calcular o preço depois fazendo uma requisição pro Catalog
                total_price = 100.00
                
                new_order = await OrderRepository.create_order(
                    session=session,
                    user_id=user_id,
                    store_id=store_id,
                    price=total_price
                )

                order_items_create = []

                for item in items_list:
                    # Pegar preço do Catalog
                    unit_price = 50.00

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

            # Implementar conexão com o catalog para decrescer o estoque dos produtos comprados

            return {'message':'Pedido gerado', 'orders_id':orders_created}
        except Exception as e:
            await session.rollback()
            print(f'Erro ao gerar o pedido: {e}')
            raise e

            
            



