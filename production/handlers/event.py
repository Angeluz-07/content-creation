from faststream.redis import RedisRouter
from context import event_service

router = RedisRouter()


@router.subscriber("download:started")
async def add_event_download_started(payload: dict):
    params = payload["params"]
    event_service.add_event(
        task_id=payload["task_id"],
        event_type="DOWNLOAD_STARTED",
        payload={"params": params},
    )


@router.subscriber("download:completed")
async def add_event_download_completed(payload: dict):
    params = payload["download"]
    event_service.add_event(
        task_id=payload["task_id"],
        event_type="DOWNLOAD_COMPLETED",
        payload={"download": params},
    )


@router.subscriber("download:failed")
async def add_event_download_failed(payload: dict):
    full_error = payload["error"]
    event_service.add_event(
        task_id=payload["task_id"],
        event_type="DOWNLOAD_FAILED",
        payload={"error": full_error},
    )
