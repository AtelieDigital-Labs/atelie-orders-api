import json
from redis.asyncio import Redis

class ShippingRepository:

    @staticmethod
    async def save_freight(redis: Redis, user_id: str, quote_json: str):
        key = f"shipping_quote:{user_id}"

        await redis.setex(name=key,time=1800,value=quote_json)

    @staticmethod
    async def get_freight(redis: Redis, user_id: str):
        key = f"shipping_quote:{user_id}"
        data = await redis.get(key)

        if data:
            return json.loads(data)
        
        return None
    
    @staticmethod
    async def delete_freight(redis: Redis, user_id: str):
        key = f"shipping_quote:{user_id}"
        await redis.delete(key)