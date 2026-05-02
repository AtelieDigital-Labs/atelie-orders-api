from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderItem


class OrderRepository:
    @staticmethod
    async def create_order(session: AsyncSession, order_data: dict):
        new_order = Order(
            user_id=order_data.user_id,
            store_id=order_data.store_id,
            price=order_data.price,
            shipping_cost=order_data.shipping_cost,
            shipping_address=order_data.shipping_address,
            shipping_method=order_data.shipping_method,
            payment_method=order_data.payment_method
        )
        
        session.add(new_order)
        await session.flush()
        
        return new_order
    
    @staticmethod
    async def create_order_items(session: AsyncSession, items_data: OrderItem):
        session.add_all(items_data)
        await session.flush()