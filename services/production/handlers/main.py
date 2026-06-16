from faststream import FastStream
from faststream.redis import RedisRouter, RedisBroker
from handlers.routes import router
from config import REDIS_URI
event_router = RedisRouter()

event_router.include_router(router)


broker = RedisBroker(REDIS_URI)
broker.include_router(event_router)
backend_worker = FastStream(broker)