from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderItem
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi_pagination.ext.sqlalchemy import paginate
from app.schemas.order import OrderArtisanStatusUpdate



class OrderRepository:
    @staticmethod
    async def update_status_order(session: AsyncSession, order: Order):
        await session.commit()

        await session.refresh(order)

        return order

    @staticmethod
    async def get_order_artisan(session: AsyncSession, order_id: int, store_id: str):
        query = select(Order).where(Order.order_id == order_id).where(Order.store_id == store_id).options(selectinload(Order.items))

        order = await session.execute(query)
        return order.scalars().first()

    @staticmethod
    async def get_all_orders_artisan(session: AsyncSession, store_id: str):
        query = select(Order).where(Order.store_id == store_id).order_by(Order.created_at.desc())

        return await paginate(session, query)

    @staticmethod
    async def get_order(session: AsyncSession, order_id: int, user_id: str):
        query = select(Order).where(Order.order_id == order_id).where(Order.user_id == user_id).options(selectinload(Order.items))

        order = await session.execute(query)
        return order.scalars().first()
    
    @staticmethod
    async def get_all_orders(session: AsyncSession, user_id: str):
        query = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        
        return await paginate(session, query)

    @staticmethod
    async def create_order(session: AsyncSession, order_data: dict):
        new_order = Order(
            user_id=order_data.user_id,
            store_id=order_data.store_id,
            price=order_data.price,
            platform_fee=order_data.platform_fee,
            checkout_group_id=order_data.checkout_group_id,
            shipping_cost=order_data.shipping_cost,
            shipping_address=order_data.shipping_address,
            shipping_method=order_data.shipping_method,
            payment_method=order_data.payment_method,
            artisan_amount=order_data.artisan_amount
        )
        
        session.add(new_order)
        await session.flush()
        
        return new_order
    
    @staticmethod
    async def create_order_items(session: AsyncSession, items_data: OrderItem):
        session.add_all(items_data)
        await session.flush()