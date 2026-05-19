from app.repositories.cart_repository import CartRepository
from redis.asyncio import Redis
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.integrations.catalog_integration import CatalogIntegration
from fastapi import HTTPException
from http import HTTPStatus



class CartService:
    @staticmethod
    async def add_item(redis: Redis, item: CartItemCreate, user_id: str):        
        data = await CatalogIntegration.fetch_all_products([item.product_variant_id])

        product_data = data.get(item.product_variant_id, {})

        available_stock = product_data.get("stock", 0) 

        current_quantity = await CartRepository.get_item_quantity(redis, user_id, item.product_variant_id)

        if (current_quantity + item.quantity) > available_stock:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=f"Estoque insuficiente. Temos apenas {available_stock} unidades disponíveis."
            )

        final_quantity = await CartRepository.increment_item(redis, user_id, item.product_variant_id, item.quantity)


        store_id = product_data.get("store_id", "default")
        unit_price = product_data.get("unit_price", 0.00) 
                
        return {
            "product_variant_id": item.product_variant_id, 
            "store_id": store_id,
            "quantity": final_quantity,
            "unit_price": unit_price
        }

    @staticmethod
    async def update_item_quantity(redis: Redis, variant_id: str, update_data: CartItemUpdate, user_id: str):
        exists = await CartRepository.item_exists(redis, user_id, variant_id)

        if not exists:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"O produto {variant_id} não foi encontrado no carrinho.")

        if update_data.quantity == 0:
            await CartRepository.remove_item(redis, user_id, variant_id)
            return {
                "product_variant_id": variant_id,
                "message": "Item removido do carrinho com sucesso.",
                "quantity": 0
            }
        
        data = await CatalogIntegration.fetch_all_products([variant_id])
        available_stock = data.get(variant_id, {}).get("stock", 0)

        if update_data.quantity > available_stock:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=f"Estoque insuficiente. Temos apenas {available_stock} unidades disponíveis."
            )

        await CartRepository.set_item_quantity(redis, user_id, variant_id, update_data.quantity)

        return {
            "product_variant_id": variant_id,
            "message": "Item atualizado com sucesso.",
            "quantity": update_data.quantity
        }

    @staticmethod
    async def get_items(redis: Redis, user_id: str):
        cart_items = await CartRepository.get_all_items(redis, user_id)

        if not cart_items:
            return{
                "items": [],
                "total_quantity": 0,
                "total_price": 0.00
            }
        
        variant_ids = list(cart_items.keys())
        
        catalog_info = await CatalogIntegration.fetch_all_products(variant_ids)

        items_list = []
        total_quantity = 0
        total_price = 0.00

        for variant_id, quantity in cart_items.items():
            product_info = catalog_info.get(variant_id, {})
            unit_price = product_info.get("unit_price", 0.00)
            
            items_list.append({
                "product_variant_id": variant_id,
                "store_id": product_info.get("store_id", "default"), 
                "quantity": quantity,
                "unit_price": unit_price
            })
            total_quantity += quantity
            total_price += (unit_price * quantity)

        return {
            "items": items_list,
            "total_quantity": total_quantity,
            "total_price": round(total_price, 2)
        }

    @staticmethod
    async def clear_cart_item(redis: Redis, item_id: str, user_id: str):
        await CartRepository.remove_item(redis, user_id, item_id)

        return{
            "message": "Produto removido do carrinho com sucesso!"
        }

    @staticmethod
    async def clear_cart(redis: Redis, user_id: str):
        await CartRepository.clear_cart(redis, user_id)

        return{
            "message": "Carrinho removido com sucesso!"
        }
