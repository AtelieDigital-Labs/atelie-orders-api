from typing import Annotated

from fastapi import Depends
from app.schemas.order import OrderCreate
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.order import OrderItem
from app.repositories.order_repository import OrderRepository


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class OrderService: 
    @staticmethod
    async def create_new_order(session: SessionDep, order_data: OrderCreate, user_id: str):
        try:
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

            
            



