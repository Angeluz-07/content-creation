import asyncio
from context import event_bus
from context import downloader
import traceback

from workers.broker import broker


@broker.task
async def download_task(task_id: str, params: dict):
    await event_bus.publish(
        "download:started", payload={"task_id": task_id, "params": params}
    )
    output_filename = params.get("output_filename")
    print(f"--- [WORKER] Iniciando proceso de: {output_filename} ---")

    try:
        await asyncio.to_thread(downloader.run, params=params)

        print(f"--- [WORKER] Finalizado con éxito: {output_filename} ---")

        await event_bus.publish(
            "download:completed", payload={"task_id": task_id, "download": params}
        )
    except Exception as e:
        print(f"--- [WORKER] Error procesando video: {str(e)} ---")
        full_error = traceback.format_exc()
        await event_bus.publish(
            "download:failed", payload={"task_id": task_id, "error": full_error}
        )
        raise e
