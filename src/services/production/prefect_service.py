from prefect.deployments import run_deployment
from typing import Dict


class PrefectService:

    async def trigger_download(self, task_id: str, data: Dict):
        print(f"Sending to download worker: {data.get('output_filename')} ")
        flow_run = await run_deployment(
            name="download/main",
            parameters={"task_id": task_id, "data": data},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

    async def trigger_discovery(self, task_id: str, data: Dict):
        print(f"Sending to discovery worker: {data.get('output_filename')} ")
        flow_run = await run_deployment(
            name="discovery/main",
            parameters={"task_id": task_id, "data": data},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )
    
    async def trigger_video_build(self, task_id: str, data: Dict):
        print(f"Sending to videobuild worker: {data.get('output_filename')} ")
        flow_run = await run_deployment(
            name="video-build/main",
            parameters={"task_id": task_id, "data": data},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

    async def trigger_ingestion(self, task_id: str, data: Dict):
        print(f"Sending to ingestion worker: {data.get('output_filename')} ")
        flow_run = await run_deployment(
            name="ingestion/main",
            parameters={"task_id": task_id, "data": data},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )