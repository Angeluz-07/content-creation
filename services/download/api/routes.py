from fastapi import APIRouter
from api.models import DownloadParamsInput, DownloadVTTInput
from context import downloader
from context import event_bus
from context import EVENTS_EMITTED
from fastapi import HTTPException
from services.utils import get_new_uuid
from workers.download import download_task

router = APIRouter(prefix="", tags=["main"])


@router.post("/download/vtt")
def download_vtt(input: DownloadVTTInput):
    print(f"Procesando vtt: {input.output_filename} desde {input.url}")
    downloader.get_vtt(
        url=input.url,
        force_download=input.force_download,
        output_filename=input.output_filename,
    )

    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {input.output_filename}",
    }


@router.post("/download-segment/synchronous")
def download_segment_synchronous(input: DownloadParamsInput):
    print(f"Procesando: {input.output_filename} desde {input.url}")
    downloader.run(params=input.model_dump())

    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {input.output_filename}",
    }


@router.post("/download-segment")
async def download_segment(input: DownloadParamsInput):
    try:
        params = input.model_dump()
        output_filename = params["output_filename"]
        task_id = get_new_uuid()

        print(f"Sending to queue: {output_filename}")

        await download_task.kiq(task_id, params)

        await event_bus.publish(
            "download:enqueued", payload={"task_id": task_id, "params": params}
        )

        return {
            "status": "queued",
            "message": f"Tarea enviada al worker para: {output_filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events-emitted")
def get_events_emitted():
    return EVENTS_EMITTED