from app.schemas.order import OrderCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import OrderItem
from app.repositories.order_repository import OrderRepository
from app.services.cart_service import CartService



class OrderService: 
    @staticmethod
    async def create_new_order(session: AsyncSession, order_data: OrderCreate, user_id: str):
        try:

            # passar os dados do carrinho para essa função, verificar o que é melhor

            items_store = {}

            for item in order_data.items:
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

            await session.commit()
            return {'message':'Pedido gerado', 'orders_id':orders_created}
        except Exception as e:
            await session.rollback()
            print(f'Erro ao gerar o pedido: {e}')
            raise e

            
            



