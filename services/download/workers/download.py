import traceback
from prefect import flow, tags
from context import downloader
from config import WEBHOOK_URI
import httpx


# trade off technical purity for simplicity of overall system
async def notify_status(flow, flow_run, state):
    if not WEBHOOK_URI:
        print("WEBHOOK_URI not defined. skipping status notification through webhook")
        return

    task_id = flow_run.parameters.get("task_id")

    task_state = state.type.value  # PENDING, RUNNING, COMPLETED, FAILED

    try:
        # Dispara y olvida: El worker no debe sufrir si la red parpadea
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                WEBHOOK_URI, json={"task_id": task_id, "status": task_state}
            )
            response.raise_for_status()

    except Exception as e:
        print(f"Couldnt notify status for task={task_id[:5]}: {e}")


@flow(
    name="download-video",  # Nombre único en el servidor
    retries=2,
    retry_delay_seconds=30,
    log_prints=True,
    timeout_seconds=600,
    on_running=[notify_status],  # status | PROCESSING
    on_completion=[notify_status],  # status | COMPLETED
    on_failure=[notify_status],  # status | FAILED
)
async def download_video(task_id: str, data: dict):
    print(f"--- [WORKER] Iniciando proceso de: {data.get("output_filename")} ---")

    try:
        await downloader.run(params=data)

        print(f"--- [WORKER] Finalizado con éxito: {data.get("output_filename")} ---")

    except Exception as e:
        print(f"--- [WORKER] Error : {str(e)} ---")
        full_error = traceback.format_exc()
        print("Full eror: ", full_error)
        raise e
