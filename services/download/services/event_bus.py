# shared/event_bus.py
import json
from redis.asyncio import Redis


class RedisEventBus:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)

    async def publish(self, event_name: str, payload: dict):
        await self.redis.publish(event_name, json.dumps(payload))


EVENTS_EMITTED = [
    {
        "name": "download:enqueued",
        "file": "api.routes.py",
        "description": "when download task is sent to worker",
        "payload": ["task_id", "params"],
    },
    {
        "name": "download:started",
        "file": "workers.download.py",
        "description": "when download task starts",
        "payload": ["task_id", "params"],
    },
    {
        "name": "download:completed",
        "file": "workers.download.py",
        "description": "when download task successfully finishes",
        "payload": ["task_id", "download"],
    },
    {
        "name": "download:failed",
        "file": "workers.download.py",
        "description": "when exception during download task",
        "payload": ["task_id", "error"],
    },
]
