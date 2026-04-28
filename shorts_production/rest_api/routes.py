from fastapi import APIRouter
from rest_api.models import ConfigInput

router = APIRouter(prefix="", tags=["main"])


@router.get("/helloworld")
def hello_world():
    return {"message": "hello world"}

@router.post("/produce-short")
def process_video(config: ConfigInput):
    # Aquí config ya es un objeto con todos los datos validados
    print(f"Procesando: {config.outname} desde {config.url}")
    
    # Lógica de negocio aquí...
    
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {config.outname}"
    }