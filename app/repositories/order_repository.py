from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderItem
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi_pagination.ext.sqlalchemy import paginate
from app.schemas.order import OrderArtisanStatusUpdate



class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_status_order(self, order: Order):
        await self.session.commit()

        await self.session.refresh(order)

        return order

    async def get_order_artisan(self, order_id: int, store_id: str):
        query = select(Order).where(Order.order_id == order_id).where(Order.store_id == store_id).where(Order.status != 'PENDING').options(selectinload(Order.items))

        order = await self.session.execute(query)
        return order.scalars().first()

    async def get_all_orders_artisan(self, store_id: str):
        query = select(Order).where(Order.store_id == store_id).where(Order.status != 'PENDING').order_by(Order.created_at.desc())

        return await paginate(self.session, query)

    async def get_order(self, order_id: int, user_id: str):
        query = select(Order).where(Order.order_id == order_id).where(Order.user_id == user_id).options(selectinload(Order.items))

        order = await self.session.execute(query)
        return order.scalars().first()
    
    async def get_all_orders(self, user_id: str):
        query = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        
        return await paginate(self.session, query)

    async def create_order(self, order_data: dict):
        new_order = Order(**order_data)
        
        self.session.add(new_order)
        await self.session.flush()
        
        return new_order
    
    async def create_order_items(self, items_data: OrderItem):
        self.session.add_all(items_data)
        await self.session.flush()

    async def get_order_group(self, group_id: str):
        query = select(Order).where(Order.checkout_group_id == group_id).options(selectinload(Order.items))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_order_group_pending(self, group_id: str):
        query = select(Order).where(Order.checkout_group_id == group_id).where(Order.status == 'PENDING')
        result = await self.session.execute(query)
        return result.scalars().all()