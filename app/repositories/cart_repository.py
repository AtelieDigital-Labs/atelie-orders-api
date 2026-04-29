from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cart import Cart, CartItem

class CartRepository:
    @staticmethod
    async def get_cart(session: AsyncSession, user_id: str):
        query = session.select(Cart).filter(Cart.user_id == user_id)
        cart = await session.execute(query)

        return cart.scalar_one_or_none()
    
    @staticmethod
    async def clear_cart_items(session: AsyncSession, cart_id: str):
        query = session.delete(CartItem).filter(CartItem.cart_id == cart_id)
        await session.execute(query)
        await session.flush()