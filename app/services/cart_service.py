from app.repositories.cart_repository import CartRepository
from redis.asyncio import Redis
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.integrations.catalog_integration import CatalogIntegration
from fastapi import HTTPException
from http import HTTPStatus



class CartService:
    # Adicionar um novo item ao carrinho ou icrementar se ele já existir
    @staticmethod
    async def add_item(redis: Redis, item: CartItemCreate, user_id: str):
        existing_item = await CartRepository.get_item(redis, user_id, item.product_variant_id)
        
        final_quantity = item.quantity
        
        if existing_item:
            final_quantity += existing_item.get("quantity", 0)

        store_id = '32' # await CatalogIntegration.get_store_id_for_product(item.product_variant_id)
            
        updated_data = {
            "quantity": final_quantity,
            "store_id": store_id
        }
        
        await CartRepository.save_item(redis, user_id, item.product_variant_id, updated_data)
        
        return {
            "product_variant_id": item.product_variant_id, 
            "store_id": updated_data['store_id'],
            "quantity": updated_data['quantity']
        }

    @staticmethod
    async def update_item_quantity(redis: Redis, variant_id: int, update_data: CartItemUpdate, user_id: str):
        existing_item = await CartRepository.get_item(redis, user_id, variant_id)

        if not existing_item:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"O item {variant_id} não foi encontrado no carrinho."
            )
        
        if update_data.quantity == 0:
            await CartRepository.remove_item(redis, user_id, variant_id)
            print("removido")
            return {
                "product_variant_id": variant_id,
                "message": "Item removido do carrinho com sucesso.",
                "quantity": 0
            }
        
        store_id = '32'#await CatalogIntegration.get_store_id_for_product(variant_id)
            
        new_data = {
            "quantity": update_data.quantity,
            "store_id": store_id
        }

        await CartRepository.save_item(redis, user_id, variant_id, new_data)

        return {
            "product_variant_id": variant_id,
            "message": "Item atualizado com sucesso.",
            "quantity": new_data["quantity"]
        }


    @staticmethod
    async def clear_cart(redis: Redis, user_id: str):
        await CartRepository.clear_cart(redis, user_id)

        return{
            "message": "Carrinho removido com sucesso!"
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
        
