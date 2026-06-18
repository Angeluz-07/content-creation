import asyncio
import traceback
from prefect import flow, tags
from context import event_bus, downloader

@flow(
    name="download-video-flow", # Nombre único en el servidor
    retries=2,
    retry_delay_seconds=30,
    log_prints=True
)
async def download_prefect_flow(task_id: str, params: dict):
    
    await event_bus.publish(
        "download:started", payload={"task_id": task_id, "params": params}
    )

    try:
        await downloader.run(params=params)
        
        await event_bus.publish(
            "download:completed", payload={"task_id": task_id, "download": params}
        )
        return {"status": "success"}

    except Exception as e:
        full_error = traceback.format_exc()
        await event_bus.publish(
            "download:failed", payload={"task_id": task_id, "error": full_error}
        )
        raise e
