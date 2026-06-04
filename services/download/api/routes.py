from fastapi import APIRouter
from api.models import DownloadParamsInput
from context import (
    download_service,
    #task_service,
)

from fastapi import HTTPException

# from context import sse_service
# from workers.download_worker import download_task

router = APIRouter(prefix="", tags=["main"])


@router.get("/download-params/last")
def get_last_download_params():

    result = download_service.get_last_download()
    return {"status": "success", "value": result}


@router.post("/download-segment/synchronous")
def download_segment_synchronous(input: DownloadParamsInput):
    print(f"Procesando: {input.output_filename} desde {input.url}")
    download_service.run(params=input.model_dump())

    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {input.output_filename}",
    }


# --- Asynchronous tasks ---
@router.post("/download-segment")
async def download_segment(input: DownloadParamsInput):
    try:
        params = input.model_dump()
        download_service.validate(params)
        params["id"] = download_service.get_new_uuid()

        output_filename = params["output_filename"]
        #task = task_service.create_task(entity_type="download", payload=params)

        print(f"Sending to queue: {output_filename}")

        # send to worker
        # await download_task.kiq(task.id, params)

        return {
            "status": "queued",
            "message": f"Tarea enviada al worker para: {output_filename}",
            #"task_id": task.id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
