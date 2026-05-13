from fastapi import APIRouter
from rest_api.models import ShortProductionParamsInput, DownloadParamsInput
from context import short_producer, downloader_service, raw_segments_filename_provider

from fastapi import HTTPException
from fastapi.responses import FileResponse
from config import TEMP_DIR, OUTPUT_DIR

router = APIRouter(prefix="", tags=["main"])

from workers.download_worker import download_task

@router.get("/helloworld")
async def hello_world():
    # .send() pone el mensaje en Redis y regresa de inmediato
    await download_task.kiq("mR stark")
    return {"message": "hello world"}

@router.post("/produce-short")
def process_video(config: ShortProductionParamsInput):
    # Aquí config ya es un objeto con todos los datos validados
    print(f"Procesando: {config.input_filename}")# todo: link data to params used for download
    print(config.model_dump())
    short_producer.run(config.model_dump())
    # Lógica de negocio aquí...
    
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {config.input_filename}"
    }


@router.get("/images/")
def get_image():
    file_path = str(TEMP_DIR/ f"debug_frame.png") 
    import os
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    
    return FileResponse(file_path)

@router.get("/video/{video_id}")
def get_video(video_id: str):
    file_path = str(OUTPUT_DIR/ f"{video_id}.mp4")
    print(file_path)
    import os
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
    print(values)
    return {
        "status": "success",
        "values": values
    }

@router.post("/download-segment")
def process_video(input: DownloadParamsInput):
    print(f"Procesando: {input.output_filename} desde {input.url}")
    downloader_service.run(params=input.model_dump())
    
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {input.output_filename}"
    }


@router.get("/download-params/last")
def get_last_download_params():

    result = downloader_service.get_last_download()
    return {
        "status": "success",
        "value": result
    }

