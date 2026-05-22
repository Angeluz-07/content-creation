import asyncio
from taskiq_redis import RedisStreamBroker
from context import (
    task_service,
    event_service,
    short_producer,
)
import traceback

broker = RedisStreamBroker("redis://localhost:6379")


@broker.task
async def short_production_task(task_id: str, params: dict):
    task_service.mark_as_processing(task_id=task_id)
    event_service.add_event(
        task_id=task_id,
        event_type="SHORT_PRODUCTION_STARTED",
        payload={"params": params},
    )
    output_filename = params.get("output_filename")
    print(f"--- [WORKER] Iniciando proceso de: {output_filename} ---")

    try:
        await asyncio.to_thread(short_producer.run, params=params)

        print(f"--- [WORKER] Finalizado con éxito: {output_filename} ---")

        event_service.add_event(
            task_id=task_id,
            event_type="SHORT_PRODUCTION_COMPLETED",
            payload={"params": params},
        )
        # short_production_projector.project(task_id=task_id)
        task_service.mark_as_completed(task_id=task_id)

    except Exception as e:
        print(f"--- [WORKER] Error procesando video: {str(e)} ---")
        full_error = traceback.format_exc()
        event_service.add_event(
            task_id=task_id,
            event_type="SHORT_PRODUCTION_FAILED",
            payload={"error": full_error},
        )
        task_service.mark_as_failed(task_id=task_id)
        raise e
