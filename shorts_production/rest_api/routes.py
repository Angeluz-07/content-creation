from fastapi import APIRouter
from rest_api.models import ConfigInput
from context import short_producer

from fastapi import HTTPException
from fastapi.responses import FileResponse
from config import TEMP_DIR

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