from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.cart_repository import CartRepository

class CartService:
    @staticmethod
    async def get_cart_items(session: AsyncSession, user_id: str):
        cart = await CartRepository.get_cart(session, user_id)

        if not cart or not cart.items:
            return None
        
        return cart.items
    
    @staticmethod
    async def clear_cart(session: AsyncSession, user_id: str):
        cart = await CartRepository.get_cart(session, user_id)

        if cart:
            await CartRepository.clear_cart_items(session, cart.cart_id)
        
