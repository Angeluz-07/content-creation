import os
from fastapi import APIRouter
from rest_api.models import ProductionInput, DownloadParamsInput
from context import (
    short_producer,
    download_service,
    raw_segments_filename_provider,
    task_service,
)

from fastapi import HTTPException
from fastapi.responses import FileResponse
from config import TEMP_DIR, OUTPUT_DIR
from sse_starlette.sse import EventSourceResponse
from context import sse_service
from workers.download_worker import download_task
from workers.short_production_worker import short_production_task

router = APIRouter(prefix="", tags=["main"])


@router.get("/helloworld")
def hello_world():
    # .send() pone el mensaje en Redis y regresa de inmediato
    return {"message": "hello world"}


@router.get("/images/")
def get_image():
    file_path = str(TEMP_DIR / f"debug_frame.png")
    import os

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    return FileResponse(file_path)

# todo: improve, this endpoint is actually for produced videos
@router.get("/video/{video_id}")
def get_video(video_id: str):
    file_path = str(OUTPUT_DIR / f"{video_id}.mp4")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video no encontrado")

    # media_type='video/mp4' es crucial para que el navegador sepa qué hacer
    return FileResponse(file_path, media_type="video/mp4")


@router.get("/video/raw/{video_id}")
def get_raw_video(video_id: str):
    file_path = raw_segments_filename_provider.get_filepath(video_id)
    import os

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video no encontrado")

    # media_type='video/mp4' es crucial para que el navegador sepa qué hacer
    return FileResponse(file_path, media_type="video/mp4")


@router.get("/video/raws/")
def get_raw_video_names():
    values = raw_segments_filename_provider.get_filenames()
    return {"status": "success", "values": values}


@router.get("/download-params/last")
def get_last_download_params():

    result = download_service.get_last_download()
    return {"status": "success", "value": result}


@router.get("/tasks")
def get_tasks(target_entity_type: str = None):
    if target_entity_type:
        result = task_service.get_all_filtered_by_type(
            target_entity_type=target_entity_type
        )
    else:
        result = task_service.get_all()
    return {"status": "success", "value": result}



# --- Explicit Synchronous tasks ---
@router.post("/download-segment/synchronous")
def download_segment_synchronous(input: DownloadParamsInput):
    print(f"Procesando: {input.output_filename} desde {input.url}")
    download_service.run(params=input.model_dump())

    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {input.output_filename}",
    }


@router.post("/produce-short/synchronous")
def process_video(config: ProductionInput):
    print(
        f"Procesando: {config.input_filename}"
    )  # todo: link data to params used for download

    short_producer.run(config.model_dump())
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {config.input_filename}",
    }


# --- Asynchronous tasks ---
@router.post("/download-segment")
async def download_segment(input: DownloadParamsInput):
    try:
        params = input.model_dump()
        download_service.validate(params)
        params["id"] = download_service.get_new_uuid()

        output_filename = params["output_filename"]
        task = task_service.create_task(entity_type="download", payload=params)

        print(f"Sending to queue: {output_filename}")

        # send to worker
        await download_task.kiq(task.id, params)

        return {
            "status": "queued",
            "message": f"Tarea enviada al worker para: {output_filename}",
            "task_id": task.id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/stream")
async def tasks_stream():
    return EventSourceResponse(sse_service.listen_task_updates_async())


@router.post("/produce-short")
async def download_segment(config: ProductionInput):
    try:
        params = config.model_dump()
        params["id"] = short_producer.get_new_uuid()
        short_producer.validator.validate(params)

        task = task_service.create_task(entity_type="short_production", payload=params)

        print(f"Sending to short_production queue: {config.input_filename}")

        await short_production_task.kiq(task.id, params)

        return {
            "status": "queued",
            "message": f"Tarea enviada al worker para: {config.input_filename}",
            "task_id": task.id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
