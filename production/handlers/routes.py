from faststream.redis import RedisRouter
from context import task_service, download_projector, sse_service

router = RedisRouter()


@router.subscriber("download:enqueued")
async def on_download_enqueued(payload: dict):
    task_id = payload["task_id"]
    params = payload["params"]
    params["id"] = task_service.get_new_uuid()  # todo: improve, not intuitive
    task_service.create_task(task_id=task_id, entity_type="download", payload=params)


@router.subscriber("download:started")
async def on_download_started(payload: dict):
    task_service.mark_as_processing(task_id=payload["task_id"])
    sse_service.notify_task_update_sync(task_id=payload["task_id"], status="PROCESSING")


@router.subscriber("download:completed")
async def on_download_completed(payload: dict):

    params = payload["download"]
    download_projector.project_direct(params=params)

    task_service.mark_as_completed(task_id=payload["task_id"])

    sse_service.notify_task_update_sync(task_id=payload["task_id"], status="COMPLETED")


@router.subscriber("download:failed")
async def on_donwload_failed(payload: dict):
    error = payload["error"]
    task_service.mark_as_failed(task_id=payload["task_id"])

    sse_service.notify_task_update_sync(task_id=payload["task_id"], status="FAILED")
