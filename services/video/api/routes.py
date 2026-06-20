from fastapi import APIRouter
from api.models import ProductionInput
from context import vb1 as video_builder
from fastapi import HTTPException
from prefect.deployments import run_deployment

router = APIRouter(prefix="", tags=["main"])


@router.post("/produce-short/synchronous")
def process_video(config: ProductionInput):
    print(f"Procesando: {config.input}")  # todo: link data to params used for download

    video_builder.run(config.model_dump())
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {config.input}",
    }


@router.post("/produce-short/prefect")
async def produce_short_prefect(data: ProductionInput):
    try:
        data = data.model_dump()
        print(f"Sending to worker: {data.get("output_filename")}")

        flow_run = await run_deployment(
            name="video-build/main",
            parameters={"task_id": data.get("task_id"), "data": data},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

        return {
            "message": f"Tarea enviada al worker para: {data.get("output")}",
        }
    except Exception as e:
        print(f"Tipo de error: {type(e)}")
        print(f"Representación (repr): {repr(e)}")

        # Si el error viene de una respuesta HTTP de la API de Prefect
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"Respuesta detallada de la API: {e.response.text}")

        raise HTTPException(status_code=400, detail=str(e))
