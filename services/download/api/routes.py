from fastapi import APIRouter
from api.models import DownloadParamsInput, DownloadVTTInput, DownloadAudioInput
from context import downloader
from context import event_bus
from context import EVENTS_EMITTED
from fastapi import HTTPException
from services.utils import get_new_uuid
from workers.download import download_video
from prefect.deployments import run_deployment

router = APIRouter(prefix="", tags=["main"])


@router.post("/download/vtt")
async def download_vtt(input: DownloadVTTInput):
    print(f"Procesando vtt: {input.output_filename} desde {input.url}")
    await downloader.get_vtt(
        url=input.url,
        force_download=input.force_download,
        output_filename=input.output_filename,
    )

    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {input.output_filename}",
    }


@router.post("/download/audio")
async def download_vtt(input: DownloadAudioInput):
    print(f"Procesando audio: {input.output_filename} desde {input.url}")
    await downloader.get_audio(
        url=input.url,
        start_ts=input.start_segment,
        end_ts=input.end_segment,
        output=input.output_filename,
        force=input.force,
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



@router.post("/download-segment/")
async def download_segment_prefect(input: DownloadParamsInput):
    try:
        params = input.model_dump()
        output_filename = params["output_filename"]
        task_id = get_new_uuid()

        print(f"Sending to queue: {output_filename}")

        flow_run = await run_deployment(
            name="download-video/main",
            parameters={"task_id": task_id, "params": params},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

        await event_bus.publish(
            "download:enqueued", payload={"task_id": task_id, "params": params}
        )

        return {
            "status": "queued",
            "backend": "prefect-native",
            "flow_run_id": str(flow_run.id),  # ID único del pipeline en Prefect
            "task_id": task_id,
            "message": f"Tarea enviada al worker para: {output_filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events-emitted")
def get_events_emitted():
    return EVENTS_EMITTED
