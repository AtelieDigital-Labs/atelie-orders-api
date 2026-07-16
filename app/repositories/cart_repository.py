from redis.asyncio import Redis

class CartRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def item_exists(self, user_id: str, variant_id: str) -> bool:
        key = f"cart:{user_id}"
        return await self.redis.hexists(key, variant_id)

    async def get_all_items(self, user_id: str) -> dict | None:
        key = f"cart:{user_id}"
        data = await self.redis.hgetall(key)
        if not data:
            return None
        
        await self.redis.expire(key, 864000)

        return {
            variant_id: int(quantity)
            for variant_id, quantity in data.items()
        }
    
    async def get_item_quantity(self, user_id: str, variant_id: str):
        key = f"cart:{user_id}"
        quantity = await self.redis.hget(key, variant_id)
        return int(quantity) if quantity else 0
    
    
    async def increment_item(self, user_id: str, variant_id: str, amount: int) -> int:
        key = f"cart:{user_id}"
        new_quantity = await self.redis.hincrby(key, variant_id, amount)

        await self.redis.expire(key, 864000)

        return new_quantity
 
    async def set_item_quantity(self, user_id: str, variant_id: str, quantity: int):
        key = f"cart:{user_id}"
        await self.redis.hset(key, variant_id, quantity)
        await self.redis.expire(key, 864000)


    async def remove_item(self, user_id: str, variant_id: str):
        await self.redis.hdel(f"cart:{user_id}", variant_id)

    async def clear_cart(self, user_id: str):
        await self.redis.delete(f"cart:{user_id}")
