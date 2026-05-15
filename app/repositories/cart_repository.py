from redis.asyncio import Redis
import json


class CartRepository:

    @staticmethod
    async def get_all_items(redis: Redis, user_id: str) -> dict | None:
        key = f"cart:{user_id}"
        data = await redis.hgetall(key)
        if not data:
            return None
        
        await redis.expire(key, 864000)

        return {
            variant_id: json.loads(item_data) 
            for variant_id, item_data in data.items()
        }
    
    @staticmethod
    async def get_item(redis: Redis, user_id: str, variant_id: str) -> dict | None:
        data = await redis.hget(f"cart:{user_id}", variant_id)
        return json.loads(data) if data else None

    @staticmethod
    async def save_item(redis: Redis, user_id: str, variant_id: str, item_data: dict):
        key = f"cart:{user_id}"
        await redis.hset(key, variant_id, json.dumps(item_data))
        await redis.expire(key, 864000)  # 10 dias em segundos

    @staticmethod
    async def remove_item(redis: Redis, user_id: str, variant_id: str):
        await redis.hdel(f"cart:{user_id}", variant_id)

    @staticmethod
    async def clear_cart(redis: Redis, user_id: str):
        await redis.delete(f"cart:{user_id}")
