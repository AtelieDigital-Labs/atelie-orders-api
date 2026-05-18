from redis.asyncio import Redis

class CartRepository:
    @staticmethod
    async def item_exists(redis: Redis, user_id: str, variant_id: str) -> bool:
        key = f"cart:{user_id}"
        return await redis.hexists(key, variant_id)

    @staticmethod
    async def get_all_items(redis: Redis, user_id: str) -> dict | None:
        key = f"cart:{user_id}"
        data = await redis.hgetall(key)
        if not data:
            return None
        
        await redis.expire(key, 864000)

        return {
            variant_id: int(quantity)
            for variant_id, quantity in data.items()
        }
    
    @staticmethod
    async def get_item_quantity(redis: Redis, user_id: str, variant_id: str):
        key = f"cart:{user_id}"
        quantity = await redis.hget(key, variant_id)
        return int(quantity) if quantity else 0
    
    
    @staticmethod
    async def increment_item(redis: Redis, user_id: str, variant_id: str, amount: int) -> int:
        key = f"cart:{user_id}"
        new_quantity = await redis.hincrby(key, variant_id, amount)

        await redis.expire(key, 864000)

        return new_quantity
 
    @staticmethod
    async def set_item_quantity(redis: Redis, user_id: str, variant_id: str, quantity: int):
        key = f"cart:{user_id}"
        await redis.hset(key, variant_id, quantity)
        await redis.expire(key, 864000)


    @staticmethod
    async def remove_item(redis: Redis, user_id: str, variant_id: str):
        await redis.hdel(f"cart:{user_id}", variant_id)


    @staticmethod
    async def clear_cart(redis: Redis, user_id: str):
        await redis.delete(f"cart:{user_id}")
