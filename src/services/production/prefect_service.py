from prefect.deployments import run_deployment
from typing import Dict


class PrefectService:

    async def trigger_download(self, task_id: str, data: Dict):
        flow_run = await run_deployment(
            name="download/main",
            parameters={"task_id": task_id, "data": data},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )

    async def trigger_discovery(self, task_id: str, data: Dict):
        flow_run = await run_deployment(
            name="discovery/main",
            parameters={"task_id": task_id, "data": data},
            timeout=0,  # IMPORTANTÍSIMO: 0 significa "encola y no te quedes esperando a que termine"
        )
