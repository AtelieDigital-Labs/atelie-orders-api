from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem


class OrderRepository:
    @staticmethod
    async def create_order(session: AsyncSession, user_id: str, store_id: str, price: float):
        new_order = Order(
            user_id=user_id,
            store_id=store_id,
            price=price
        )
        
        session.add(new_order)
        await session.flush()
        
        return new_order
    
    @staticmethod
    async def create_order_items(session: AsyncSession, items_data: OrderItem):
        session.add_all(items_data)
        await session.flush()