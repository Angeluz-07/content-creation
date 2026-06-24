from fastapi import APIRouter
from api.models import DiscoveryInput
from context import metal_detector
from fastapi import HTTPException
from prefect.deployments import run_deployment

router = APIRouter(prefix="", tags=["main"])


@router.post("/discovery/vtt")
async def download_vtt(data: DiscoveryInput):
    print(f"Procesando vtt: {data.input_filename}")
    metal_detector.run(data.model_dump())
    return {
        "status": "success",
        "message": f"Procesamiento iniciado para {data.output_filename}",
    }


# @router.post("/download")
# async def download_video(data: DownloadInput):
#     try:
#         data = data.model_dump()
#         print(f"Sending to worker: {data.get("output_filename")}")

#         flow_run = await run_deployment(
#             name="download/main",
#             parameters={"task_id": data.get("task_id"), "data": data},
#             timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
#         )

#         return {
#             "message": f"Tarea enviada al worker para: {data.get("output_filename")}",
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
