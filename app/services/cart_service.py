from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.cart_repository import CartRepository
from redis.asyncio import Redis
from app.schemas.cart import CartItemCreate


class CartService:
    
    # verificar se volto a receber redis: Redis
    def __init__(self, repo: CartRepository):
        self._repo = repo

    # Adicionar um novo item ao carrinho ou icrementar se ele já existir
    async def add_item(self, item: CartItemCreate, user_id: str):
        existing_item = await self._repo.get_item(user_id, item.variant_id)
        
        final_quantity = item.quantity
        
        if existing_item:
            final_quantity += existing_item.get("quantity", 0)
            
        updated_data = {
            "quantity": final_quantity,
        }
        
        await self._repo.save_item(user_id, item.variant_id, updated_data)
        
        return {
            "variant_id": item.variant_id, 
            "store_id": item.store_id,
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
        
