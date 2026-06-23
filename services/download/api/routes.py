from fastapi import APIRouter
from api.models import (
    DownloadAudioInput,
    DownloadInput,
)
from context import downloader
from fastapi import HTTPException
from prefect.deployments import run_deployment

router = APIRouter(prefix="", tags=["main"])


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


@router.post("/download")
async def download_video(data: DownloadInput):
    try:
        data = data.model_dump()
        print(f"Sending to worker: {data.get("output_filename")}")

        flow_run = await run_deployment(
            name="download/main",
            parameters={"task_id": data.get("task_id"), "data": data},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

        return {
            "message": f"Tarea enviada al worker para: {data.get("output_filename")}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
