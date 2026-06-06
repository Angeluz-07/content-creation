from fastapi import APIRouter
from api.models import ProductionInput
from context import production_service as video_builder
from context import event_bus
#from context import EVENTS_EMITTED
from fastapi import HTTPException
#from services.utils import get_new_uuid
#from workers.download import download_task

router = APIRouter(prefix="", tags=["main"])



@router.post("/produce-short/synchronous")
def process_video(config: ProductionInput):
    print(
        f"Procesando: {config.input_filename}"
    )  # todo: link data to params used for download

    video_builder.run(config.model_dump())
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {config.input_filename}",
    }


# @router.post("/produce-short")
# async def download_segment(config: ProductionInput):
#     try:
#         params = config.model_dump()
#         params["id"] = short_producer.get_new_uuid()
#         short_producer.validator.validate(params)

#         task = task_service.create_task(entity_type="short_production", payload=params)

#         print(f"Sending to short_production queue: {config.input_filename}")

#         await short_production_task.kiq(task.id, params)

#         return {
#             "status": "queued",
#             "message": f"Tarea enviada al worker para: {config.input_filename}",
#             "task_id": task.id,
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/events-emitted")
# def get_events_emitted():
#     return EVENTS_EMITTED