from faststream.redis import RedisRouter
from context import task_service

router = RedisRouter()

@router.subscriber("download:enqueued")
async def create_task(payload: dict):
    task_id = payload["task_id"]
    params = payload["params"]
    params["id"] = task_id
    task_service.create_task(entity_type="download", payload=params)

@router.subscriber("download:started")
async def mask_task_as_processing(payload: dict):
    task_service.mark_as_processing(task_id=payload["task_id"])

@router.subscriber("download:completed")
async def mask_task_as_completed(payload: dict):
    task_service.mark_as_completed(task_id=payload["task_id"])

@router.subscriber("download:failed")
async def mask_task_as_failed(payload: dict):
    task_service.mark_as_failed(task_id=payload["task_id"])