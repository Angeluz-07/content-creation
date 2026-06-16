import asyncio
import json
import redis  # Cliente síncrono estándar
import redis.asyncio as aioredis  # Cliente asíncrono
from typing import AsyncGenerator

class SSEService:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.channel_name = "task_updates"
        
        # Cliente síncrono para el TaskService / Workers síncronos
        self.redis_sync = redis.from_url(redis_url)
        
        # Cliente asíncrono para el endpoint SSE de la API
        self.redis_async = aioredis.from_url(redis_url)

    def notify_task_update_sync(self, task_id: str, status: str) -> None:
        """
        Método SÍNCRONO para publicar en Redis. 
        Ideal para llamarlo desde repositorios o servicios síncronos.
        """
        payload = {
            "task_id": task_id,
            "status": status
        }
        # Operación síncrona ultra veloz
        self.redis_sync.publish(self.channel_name, json.dumps(payload))

    async def listen_task_updates_async(self) -> AsyncGenerator[dict, None]:
        """
        Método ASÍNCRONO para escuchar eventos. 
        Usado exclusivamente por el endpoint SSE de FastAPI.
        """
        pubsub = self.redis_async.pubsub()
        await pubsub.subscribe(self.channel_name)
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield {
                        "event": "update",
                        "data": message["data"].decode("utf-8")
                    }
        except asyncio.CancelledError:
            await pubsub.unsubscribe(self.channel_name)
