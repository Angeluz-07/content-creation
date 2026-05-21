import asyncio
from taskiq_redis import RedisStreamBroker
from context import downloader_service, task_service, event_service

# 1. Usamos la clase que la librería encontró
broker = RedisStreamBroker("redis://localhost:6379")


@broker.task
async def download_task(task_id: str, params: dict):
    task_service.mark_as_processing(task_id=task_id)
    event_service.add_event(
        task_id=task_id, event_type="DOWNLOAD_STARTED", payload={"params": params}
    )
    output_filename = params.get("output_filename")
    print(f"--- [WORKER] Iniciando proceso de: {output_filename} ---")

    try:
        result = await asyncio.to_thread(downloader_service.run, params=params)

        print(f"--- [WORKER] Finalizado con éxito: {output_filename} ---")

        event_service.add_event(
            task_id=task_id,
            event_type="DOWNLOAD_COMPLETED",
            payload={"download_id": result},
        )
        # todo: service to project data
        task_service.mark_as_completed(task_id=task_id)
        return result
    except Exception as e:
        print(f"--- [WORKER] Error procesando video: {str(e)} ---")
        event_service.add_event(
            task_id=task_id, event_type="DOWNLOAD_FAILED", payload={"error": str(e)}
        )
        task_service.mark_as_failed(task_id=task_id)
        raise e
