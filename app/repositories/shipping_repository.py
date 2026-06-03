import json
from redis.asyncio import Redis

class ShippingRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def save_freight(self, user_id: str, quote_json: str):
        key = f"shipping_quote:{user_id}"

        await self.redis.setex(name=key,time=1800,value=quote_json)

    async def get_freight(self, user_id: str):
        key = f"shipping_quote:{user_id}"
        data = await self.redis.get(key)

        if data:
            return json.loads(data)
        
        return None

    async def delete_freight(self, user_id: str):
        key = f"shipping_quote:{user_id}"
        await self.redis.delete(key)