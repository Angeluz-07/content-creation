import asyncio
from context import event_bus
from context import video_builder
import traceback
from workers.broker import broker

@broker.task
async def video_build_task(task_id: str, params: dict):
    await event_bus.publish(
        "video_build:started", payload={"task_id": task_id, "params": params}
    )
    output_filename = params.get("output_filename")
    print(f"--- [WORKER] Iniciando proceso de: {output_filename} ---")

    try:
        await asyncio.to_thread(video_builder.run, params=params)

        print(f"--- [WORKER] Finalizado con éxito: {output_filename} ---")

        await event_bus.publish(
            "video_build:completed", payload={"task_id": task_id, "params": params}
        )
    except Exception as e:
        print(f"--- [WORKER] Error procesando video: {str(e)} ---")
        full_error = traceback.format_exc()
        await event_bus.publish(
            "video_build:failed", payload={"task_id": task_id, "error": full_error}
        )
        raise e
