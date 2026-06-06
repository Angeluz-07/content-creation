from faststream.redis import RedisRouter
from context import task_service, download_projector, sse_service
from context import short_production_projector

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


# ---


@router.subscriber("video_build:enqueued")
async def on_video_build_enqueued(payload: dict):
    task_id = payload["task_id"]
    params = payload["params"]
    params["id"] = task_service.get_new_uuid()  # todo: improve, not intuitive
    task_service.create_task(
        task_id=task_id, entity_type="short_production", payload=params
    )


@router.subscriber("video_build:started")
async def on_video_build_started(payload: dict):
    task_service.mark_as_processing(task_id=payload["task_id"])
    sse_service.notify_task_update_sync(task_id=payload["task_id"], status="PROCESSING")


@router.subscriber("video_build:completed")
async def on_video_build_completed(payload: dict):

    params = payload["params"]
    short_production_projector.project_direct(params=params)

    task_service.mark_as_completed(task_id=payload["task_id"])

    sse_service.notify_task_update_sync(task_id=payload["task_id"], status="COMPLETED")


@router.subscriber("video_build:failed")
async def on_video_build_failed(payload: dict):
    error = payload["error"]
    task_service.mark_as_failed(task_id=payload["task_id"])

    sse_service.notify_task_update_sync(task_id=payload["task_id"], status="FAILED")
