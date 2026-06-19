from fastapi import APIRouter
from api.models import ProductionInput
from context import vb1 as video_builder
from context import event_bus

# from context import EVENTS_EMITTED
from fastapi import HTTPException
from services.utils import get_new_uuid
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
async def produce_short_prefect(config: ProductionInput):
    try:
        print("hello", config)
        params = config.model_dump()
        output_filename = params["output"]
        task_id = get_new_uuid()

        print(f"Sending to queue: {output_filename}")

        flow_run = await run_deployment(
            name="video-build/main",
            parameters={"task_id": task_id, "params": params},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

        await event_bus.publish(
            "video_build:enqueued", payload={"task_id": task_id, "params": params}
        )

        return {
            "status": "queued",
            "backend": "prefect-native",
            "flow_run_id": str(flow_run.id),  # ID único del pipeline en Prefect
            "task_id": task_id,
            "message": f"Tarea enviada al worker para: {output_filename}",
        }
    except Exception as e:
        print(f"Tipo de error: {type(e)}")
        print(f"Representación (repr): {repr(e)}")

        # Si el error viene de una respuesta HTTP de la API de Prefect
        if hasattr(e, "response") and hasattr(e.response, "text"):
            print(f"Respuesta detallada de la API: {e.response.text}")

        raise HTTPException(status_code=400, detail=str(e))


# @router.get("/events-emitted")
# def get_events_emitted():
#     return EVENTS_EMITTED
