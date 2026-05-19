import asyncio
from taskiq_redis import RedisStreamBroker 
from context import downloader_service, task_service

# 1. Usamos la clase que la librería encontró
broker = RedisStreamBroker("redis://localhost:6379")

@broker.task
async def download_task(task_id: str, params: dict):
    task_service.mark_as_processing(task_id=task_id)

    output_filename = params.get('output_filename')
    print(f"--- [WORKER] Iniciando proceso de: {output_filename} ---")
    
    # Usamos to_thread para que el subprocess.run del servicio legacy
    # no congele el hilo principal del worker.
    try:
        result = await asyncio.to_thread(
            downloader_service.run, 
            params=params
        )
        print(f"--- [WORKER] Finalizado con éxito: {output_filename} ---")
        task_service.mark_as_completed(task_id=task_id)
        return result
    except Exception as e:
        print(f"--- [WORKER] Error procesando video: {str(e)} ---")
        task_service.mark_as_failed(task_id=task_id)
        raise e