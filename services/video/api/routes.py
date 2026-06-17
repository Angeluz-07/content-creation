from fastapi import APIRouter
from api.models import ProductionInput
from context import vb1 as video_builder
from context import event_bus

# from context import EVENTS_EMITTED
from fastapi import HTTPException
from services.utils import get_new_uuid
from workers.video_build import video_build_task

router = APIRouter(prefix="", tags=["main"])


@router.post("/produce-short/synchronous")
def process_video(config: ProductionInput):
    print(
        f"Procesando: {config.input}"
    )  # todo: link data to params used for download

    video_builder.run(config.model_dump())
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {config.input}",
    }


@router.post("/produce-short")
async def download_segment(config: ProductionInput):
    try:
        params = config.model_dump()
        task_id = get_new_uuid()
        print(f"Sending to queue: {config.input}")
        await video_build_task.kiq(task_id, params)

        await event_bus.publish(
            "video_build:enqueued", payload={"task_id": task_id, "params": params}
        )
        return {
            "status": "queued",
            "message": f"Tarea enviada al worker para: {config.input}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.get("/events-emitted")
# def get_events_emitted():
#     return EVENTS_EMITTED
