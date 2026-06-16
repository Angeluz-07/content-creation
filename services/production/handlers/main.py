from faststream import FastStream
from faststream.redis import RedisRouter, RedisBroker
from handlers.routes import router

event_router = RedisRouter()

event_router.include_router(router)


broker = RedisBroker("redis://localhost:6379/0")
broker.include_router(event_router)
backend_worker = FastStream(broker)