import os
from fastapi import APIRouter
from rest_api.models import ShortProductionParamsInput, DownloadParamsInput
from context import (
    short_producer,
    downloader_service,
    raw_segments_filename_provider,
    task_service,
)

from fastapi import HTTPException
from fastapi.responses import FileResponse
from config import TEMP_DIR, OUTPUT_DIR
from sse_starlette.sse import EventSourceResponse
from context import sse_service
from workers.download_worker import download_task

router = APIRouter(prefix="", tags=["main"])


@router.get("/helloworld")
def hello_world():
    # .send() pone el mensaje en Redis y regresa de inmediato
    return {"message": "hello world"}


@router.post("/produce-short")
def process_video(config: ShortProductionParamsInput):
    print(
        f"Procesando: {config.input_filename}"
    )  # todo: link data to params used for download

    short_producer.run(config.model_dump())
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {config.input_filename}",
    }


@router.get("/images/")
def get_image():
    file_path = str(TEMP_DIR / f"debug_frame.png")
    import os

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    return FileResponse(file_path)


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


@router.post("/download-segment/synchronous")
def download_segment_synchronous(input: DownloadParamsInput):
    print(f"Procesando: {input.output_filename} desde {input.url}")
    downloader_service.run(params=input.model_dump())

    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {input.output_filename}",
    }


@router.get("/download-params/last")
def get_last_download_params():

    result = downloader_service.get_last_download()
    return {"status": "success", "value": result}


@router.get("/tasks")
def get_tasks():
    result = task_service.get_all()
    return {"status": "success", "value": result}

@router.get("/tasks/agg")
def get_tasks_aggregated():
    result = task_service.get_all_aggregated()
    return {"status": "success", "value": result}

# --- Asynchronous tasks ---
@router.post("/download-segment")
async def download_segment(input: DownloadParamsInput):
    try: 
        params = input.model_dump()
        download = downloader_service.create_download(params)
        output_filename = download.output_filename
        task = task_service.create_task(target_id=download.id)

        print(f"Sending to queue: {output_filename}")

        # send to worker
        await download_task.kiq(task.id, params)
              
        return {
            "status": "queued",
            "message": f"Tarea enviada al worker para: {output_filename}",
            "task_id": task.id,
            "download_id": download.id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/tasks/stream")
async def tasks_stream():
    return EventSourceResponse(sse_service.listen_task_updates_async())