from fastapi import APIRouter
from rest_api.models import ConfigInput, DownloadParamsInput
from context import short_producer, downloader_service

from fastapi import HTTPException
from fastapi.responses import FileResponse
from config import TEMP_DIR, OUTPUT_DIR

router = APIRouter(prefix="", tags=["main"])


@router.get("/helloworld")
def hello_world():
    return {"message": "hello world"}

@router.post("/produce-short")
def process_video(config: ConfigInput):
    # Aquí config ya es un objeto con todos los datos validados
    print(f"Procesando: {config.outname} desde {config.url}")
    short_producer.run(config.model_dump())
    # Lógica de negocio aquí...
    
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {config.outname}"
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

@router.post("/download-segment")
def process_video(input: DownloadParamsInput):
    print(f"Procesando: {input.filename} desde {input.url}")
    downloader_service.run(params=input.model_dump())
    
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {input.filename}"
    }
