from redis.asyncio import Redis
import json


class CartRepository:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def get_all_items(self, user_id: str) -> dict | None:
        data = await self._redis.hgetall(f"cart:{user_id}")
        if not data:
            return None
        
        return {
            variant_id: json.loads(item_data) 
            for variant_id, item_data in data.items()
        }

    async def get_item(self, user_id: str, variant_id: str) -> dict | None:
        data = await self._redis.hget(f"cart:{user_id}", variant_id)
        return json.loads(data) if data else None

    async def save_item(self, user_id: str, variant_id: str, item_data: dict):
        key = f"cart:{user_id}"
        await self._redis.hset(key, variant_id, json.dumps(item_data))
        await self._redis.expire(key, 864000)  # 10 dias em segundos

    async def remove_item(self, user_id: str, variant_id: str):
        await self._redis.hdel(f"cart:{user_id}", variant_id)

    async def clear_cart(self, user_id: str):
        await self._redis.delete(f"cart:{user_id}")

    # @staticmethod
    # async def get_cart(session: AsyncSession, user_id: str):
    #     query = select(Cart).filter(Cart.user_id == user_id)
    #     cart = await session.execute(query)

    #     return cart.scalar_one_or_none()
    
    # @staticmethod
    # async def clear_cart_items(session: AsyncSession, cart_id: str):
    #     query = session.delete(CartItem).filter(CartItem.cart_id == cart_id)
    #     await session.execute(query)
