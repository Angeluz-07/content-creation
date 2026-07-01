import os
from fastapi import APIRouter
from .models import ProductionInput, DownloadParamsInput, DownloadInput, DiscoveryInput
from src.context.production import (
    short_producer,
    download_service,
    raw_segments_filename_provider,
    task_service,
    assets,
    discovery_service,
)

from fastapi import HTTPException
from fastapi.responses import FileResponse
from src.config import TEMP_DIR, OUTPUT_DIR
from src.context.production import task_service, download_service
from pathlib import Path
from .models import TaskSyncInput

router = APIRouter(prefix="", tags=["main"])


@router.post("/tasks/sync")
def sync_task_status(data: TaskSyncInput):
    print("testing hook", data.task_id, data.status)
    new_status = data.status
    task_id = data.task_id
    if new_status == "RUNNING":
        task_service.mark_as_processing(task_id)
    elif new_status == "COMPLETED":
        # todo: project domain object by entity_type
        task_service.mark_as_completed(task_id)
    elif new_status == "FAILED":
        task_service.mark_as_failed(task_id)
    else:
        print("unknown state for", task_id)
    return {"status": "success"}


@router.get("/helloworld")
def hello_world():
    # .send() pone el mensaje en Redis y regresa de inmediato
    return {"message": "hello worldd"}


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


@router.get("/assets/vtt")
def get_raw_video_names():
    values = assets.list_files("vtt")
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


from prefect.deployments import run_deployment


@router.post("/download")
async def download_video(data: DownloadInput):
    try:
        params = data.model_dump()
        download_service.validate(params)

        new_task_id = task_service.get_new_uuid()  # todo: improve, not intuitive
        params["id"] = task_service.get_new_uuid()
        params["task_id"] = new_task_id
        task_service.create_task(
            task_id=new_task_id, entity_type="download", payload=params
        )
        flow_run = await run_deployment(
            name="download/main",
            parameters={"task_id": params.get("task_id"), "data": params},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

        return {
            "message": f"Tarea enviada al worker para: {params.get("output_filename")}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/discovery")
async def discovery(data: DiscoveryInput):
    try:
        params = data.model_dump()
        new_task_id = task_service.get_new_uuid()  # todo: improve, not intuitive
        params["id"] = task_service.get_new_uuid()
        params["task_id"] = new_task_id
        task_service.create_task(
            task_id=new_task_id, entity_type="discovery", payload=params
        )

        flow_run = await run_deployment(
            name="discovery/main",
            parameters={"task_id": params.get("task_id"), "data": params},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )
        print(f"Sending to discovery service: {data.output_filename} ")

        return {
            "message": f"Sent to discovery: {params["output_filename"]}",
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


from datetime import datetime, timedelta
import math


def format_time(time_str, round_fn, extra_sec=0):
    # Convertimos el string en un objeto timedelta para manipularlo fácilmente
    t = datetime.strptime(time_str, "%H:%M:%S.%f")
    seconds = t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
    # Aplicamos el redondeo (piso o techo) y los segundos extra
    final_seconds = round_fn(seconds) + extra_sec
    return str(timedelta(seconds=final_seconds)).zfill(8)


def map_discovery_results(result, prefix):
    # Fecha de hoy en formato AAAAMMDD
    today = datetime.now().strftime("%Y%m%d")

    # Mapeo compacto en una sola línea de comprensión (list comprehension)
    mapped_data = [
        {
            "start_segment": format_time(item["start"], math.floor),
            "end_segment": format_time(item["end"], math.ceil, extra_sec=1),
            "text": item["full_context"],
            "output_filename": f"{prefix}_{idx:02d}",
            "force_download": False,
            "url": item["url"],
        }
        for idx, item in enumerate(result)
    ]
    return mapped_data


@router.get("/discovery/results/{result_id}")
def get_discovery_result(result_id: str):
    values = assets.get_path("metals", result_id)
    import json

    with open(values, "r", encoding="utf-8") as file:
        file_content = json.load(file)
    result = map_discovery_results(file_content, result_id)
    return {"status": "success", "values": result}


@router.post("/discovery/results/{result_id}/trigger-download")
async def get_discovery_result(result_id: str):
    values = assets.get_path("metals", result_id)
    import json

    with open(values, "r", encoding="utf-8") as file:
        file_content = json.load(file)
    result = map_discovery_results(file_content, result_id)
    # print(result)
    for item in result:
        params = {}
        params["file_type"] = "video"
        params["url"] = item["url"]
        params["force_download"] = item["force_download"]
        params["start_segment"] = item["start_segment"]
        params["end_segment"] = item["end_segment"]
        params["output_filename"] = item["output_filename"]
        new_task_id = task_service.get_new_uuid()  # todo: improve, not intuitive
        params["id"] = task_service.get_new_uuid()
        params["task_id"] = new_task_id
        try:
            download_service.validate(params)
        except Exception as e:
            print("Exception: ", str(e))
            print(f"Skipping triggering for {item["output_filename"]}")
            continue  # to next iteration

        task_service.create_task(
            task_id=new_task_id, entity_type="download", payload=params
        )
        flow_run = await run_deployment(
            name="download/main",
            parameters={"task_id": params.get("task_id"), "data": params},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

        print(f"Sending to download service: {item["output_filename"]} ")
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
        flow_run = await run_deployment(
            name="video-build/main",
            parameters={"task_id": params.get("task_id"), "data": params},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

        print(f"Sending to video worker: {config.input_filename}")

        return {
            "message": f"Sent to video_build: {config.input_filename}",
        }
    except Exception as e:
        print(f"Tipo de error: {type(e)}")
        print(f"Representación (repr): {repr(e)}")

        # Si el error viene de una respuesta HTTP de la API de Prefect
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"Respuesta detallada de la API: {e.response.text}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ingestion/{folder_name}")
def ingestion(folder_name: str):
    # .send() pone el mensaje en Redis y regresa de inmediato
    return {"message": "ok"}
