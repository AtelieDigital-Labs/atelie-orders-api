from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.cart_repository import CartRepository
from redis.asyncio import Redis
from app.schemas.cart import CartItemCreate


class CartService:

    # Adicionar um novo item ao carrinho ou icrementar se ele já existir
    async def add_item(redis: Redis, item: CartItemCreate, user_id: str):
        existing_item = await CartRepository.get_item(redis, user_id, item.product_variant_id)
        
        final_quantity = item.quantity
        
        if existing_item:
            final_quantity += existing_item.get("quantity", 0)
            
        updated_data = {
            "quantity": final_quantity,
            "store_id": '1'
        }
        
        await CartRepository.save_item(redis, user_id, item.product_variant_id, updated_data)
        
        return {
            "product_variant_id": item.product_variant_id, 
            "store_id": '1',
            "quantity": updated_data['quantity']
        }

    # @staticmethod
    # async def get_cart_items(session: AsyncSession, user_id: str):
    #     cart = await CartRepository.get_cart(session, user_id)

    #     if not cart or not cart.items:
    #         return None
        
    #     return cart.items
    
    # @staticmethod
    # async def clear_cart(session: AsyncSession, user_id: str):
    #     cart = await CartRepository.get_cart(session, user_id)

    #     if cart:
    #         await CartRepository.clear_cart_items(session, cart.cart_id)
        
