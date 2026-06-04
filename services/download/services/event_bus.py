# shared/event_bus.py
import json
from redis.asyncio import Redis

class RedisEventBus:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)

    async def publish(self, event_name: str, payload: dict):
        await self.redis.publish(event_name, json.dumps(payload))