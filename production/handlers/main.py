from faststream import FastStream
from faststream.redis import RedisRouter, RedisBroker
from handlers.task import router as task_router
from handlers.download import router as download_router
from handlers.event import router as event_router_

event_router = RedisRouter()

event_router.include_router(task_router)
event_router.include_router(download_router)
event_router.include_router(event_router_)


broker = RedisBroker("redis://localhost:6379/0")
broker.include_router(event_router)
backend_worker = FastStream(broker)