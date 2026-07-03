from fastapi import APIRouter
from .models import ProductionInput, DownloadInput, DiscoveryInput
from src.context.common import assets
from src.services.common.utils import read_json

from src.context.production import prefect_service
from src.context.production import (
    short_producer,
    download_service,
    task_service,
)

from fastapi import HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from .models import TaskSyncInput

router = APIRouter(prefix="", tags=["main"])


@router.get("/helloworld")
def hello_world():
    return {"message": "hello world"}


@router.get("/images/")
def get_image():
    file_path = assets.get_path("temp", "debug_frame.png")
    if not Path(file_path).is_file():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    return FileResponse(file_path)


# todo: improve, this endpoint is actually for produced videos
@router.get("/video/{video_id}")
def get_video(video_id: str):
    file_path = assets.get_path("output_videos", f"{video_id}.mp4")
    if not Path(file_path).is_file():
        raise HTTPException(status_code=404, detail="Video no encontrado")

    # media_type='video/mp4' es crucial para que el navegador sepa qué hacer
    return FileResponse(file_path, media_type="video/mp4")


@router.get("/video/raw/{video_id}")
def get_raw_video(video_id: str):
    file_path = assets.get_path("input", f"{video_id}.mp4")

    if not Path(file_path).is_file():
        raise HTTPException(status_code=404, detail="Video no encontrado")

    # media_type='video/mp4' es crucial para que el navegador sepa qué hacer
    return FileResponse(file_path, media_type="video/mp4")


@router.get("/video/raws/")
def get_raw_video_names():
    values = assets.get_filenames("input")
    return {"status": "success", "values": values}


@router.get("/assets/vtt")
def get_vtt_names():
    values = assets.get_filenames("vtt")
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


@router.post("/tasks/sync")
def sync_task_status(data: TaskSyncInput):
    task_service.update_status(data.task_id, data.status)
    return {"status": "success"}


@router.post("/download")
async def download_video(data: DownloadInput):
    try:
        data = data.model_dump()
        download_service.validate(data)

        task_id = task_service.create_task(entity_type="download", payload=data)
        await prefect_service.trigger_download(task_id, data)
        return {
            "message": f"Sent to download: {data.get("output_filename")}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/discovery")
async def discovery(data: DiscoveryInput):
    try:
        data = data.model_dump()
        task_id = task_service.create_task(entity_type="discovery", payload=data)
        await prefect_service.trigger_discovery(task_id, data)
        return {
            "message": f"Sent to discovery: {data.get('output_filename')}",
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/produce-short")
async def process_video_async(data: ProductionInput):
    try:
        data = data.model_dump()
        short_producer.validate(data)
        task_id = task_service.create_task(entity_type="short_production", payload=data)

        await prefect_service.trigger_video_build(task_id, data)
        return {
            "message": f"Sent to video_build: {data.get('output_filename')}",
        }
    except Exception as e:
        print(f"Tipo de error: {type(e)}")
        print(f"Representación (repr): {repr(e)}")

        # Si el error viene de una respuesta HTTP de la API de Prefect
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"Respuesta detallada de la API: {e.response.text}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ingestion/{folder_name}")
async def ingestion(folder_name: str):
    try:
        data = {"folder_name": folder_name}
        task_id = task_service.create_task(entity_type="ingestion", payload=data)
        await prefect_service.trigger_ingestion(task_id, data)
        return {"message": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/discovery/results/{result_id}")
def get_discovery_result(result_id: str):
    filepath = assets.get_path("metals", result_id)
    result = read_json(filepath)
    return {"status": "success", "values": result}


@router.post("/discovery/results/{result_id}/trigger-download")
async def trigger_download_for_discovery_result(result_id: str):
    filepath = assets.get_path("metals", result_id)
    result = read_json(filepath)

    for data in result:
        task_id = task_service.create_task(entity_type="download", payload=data)
        await prefect_service.trigger_download(task_id, data)

        print(f"Sending to download service: {data.get("output_filename")}")
    return {"status": "success"}


# todo: migrate
# @router.post("/produce-short/synchronous")
# def process_video(config: ProductionInput):
#     print(f"Procesando: {config.input}")  # todo: link data to params used for download

#     video_builder.run(config.model_dump())
#     return {
#         "status": "success",
#         "message": f"Procesamiento iniciado para {config.input}",
#     }
