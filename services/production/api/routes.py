import os
from fastapi import APIRouter
from api.models import ProductionInput, DownloadParamsInput, DownloadInput
from context import (
    short_producer,
    download_service,
    raw_segments_filename_provider,
    task_service,
)

from fastapi import HTTPException
from fastapi.responses import FileResponse
from config import TEMP_DIR, OUTPUT_DIR
from context import task_service, download_service
from pathlib import Path
from api.models import TaskSyncInput

router = APIRouter(prefix="", tags=["main"])


@router.post("/tasks/sync")
def sync_task_status(data: TaskSyncInput):
    print("testing hook", data.task_id, data.status)
    new_status = data.status
    task_id = data.task_id
    if new_status == "RUNNING":
        task_service.mark_as_processing(task_id)
    elif new_status == "COMPLETED":
        #todo: project domain object by entity_type
        task_service.mark_as_completed(task_id)
    elif new_status == "FAILED":
        task_service.mark_as_failed(task_id)
    else:
        print("unknown state for", task_id)
    return {"status": "success"}

@router.get("/helloworld")
def hello_world():
    # .send() pone el mensaje en Redis y regresa de inmediato
    return {"message": "hello world"}


@router.get("/images/")
def get_image():
    file_path = str(Path(TEMP_DIR) / f"debug_frame.png")
    import os

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    return FileResponse(file_path)


# todo: improve, this endpoint is actually for produced videos
@router.get("/video/{video_id}")
def get_video(video_id: str):
    file_path = str(Path(OUTPUT_DIR) / f"{video_id}.mp4")
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


# --- Asynchronous tasks ---
@router.post("/download")
async def download_segment(config: DownloadInput):
    try:
        params = config.model_dump()
        download_service.validate(params)
        new_task_id = task_service.get_new_uuid()  # todo: improve, not intuitive
        params["id"] = task_service.get_new_uuid() 
        params["task_id"] = new_task_id
        task_service.create_task(
            task_id=new_task_id, entity_type="download", payload=params
        )
        download_service.trigger(params)
        print(f"Sending to download service: {config.output_filename} ")

        return {
            "message": f"Sent to download: {params["output_filename"]}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# todo colapse into single method
@router.post("/produce-short/synchronous")
def process_video(config: ProductionInput):
    print(
        f"Procesando: {config.input}"
    )  # todo: link data to params used for download
    
    short_producer.trigger_sync(config.model_dump())
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {config.input}",
    }


@router.post("/produce-short")
async def process_video_async(config: ProductionInput):
    try:
        params = config.model_dump()
        short_producer.validate(params)
        new_task_id = task_service.get_new_uuid()  # todo: improve, not intuitive
        params["id"] = task_service.get_new_uuid() 
        params["task_id"] = new_task_id
        task_service.create_task(
            task_id=new_task_id, entity_type="short_production", payload=params
        )
        short_producer.trigger_async(params)

        print(f"Sending to short_production queue: {config.input_filename}")

        return {
            "message": f"Sent to video_build: {config.input_filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
