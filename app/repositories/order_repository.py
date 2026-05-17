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
        new_order = Order(**order_data)
        
        session.add(new_order)
        await session.flush()
        
        return new_order
    
    @staticmethod
    async def create_order_items(session: AsyncSession, items_data: OrderItem):
        session.add_all(items_data)
        await session.flush()


    @staticmethod
    async def get_order_group(session: AsyncSession, group_id: str):
        query = select(Order).where(Order.checkout_group_id == group_id).options(selectinload(Order.items))
        result = await session.execute(query)
        return result.scalars().all()