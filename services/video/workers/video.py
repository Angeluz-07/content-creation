import traceback
from prefect import flow, tags
from context import event_bus
from context import vb1 as video_builder


@flow(
    name="video-build",  # Nombre único en el servidor
    retries=2,
    retry_delay_seconds=30,
    log_prints=True,
    timeout_seconds=600,
)
async def video_build(task_id: str, params: dict):
    await event_bus.publish(
        "video_build:started", payload={"task_id": task_id, "params": params}
    )
    output_filename = params.get("output")
    print(f"--- [WORKER] Iniciando proceso de: {output_filename} ---")

    try:
        await video_builder.run_async(params=params)

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
