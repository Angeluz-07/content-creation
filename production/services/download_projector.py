from dbs.mongo_repository import EventMongoRepository
from dbs.interfaces import IRepository
from domain.models import Download
from typing import Dict

class DownloadProjector:

    def __init__(self, event_repo, download_repo):
        self.event_repo: EventMongoRepository = event_repo
        self.download_repo: IRepository = download_repo

    def project(self, task_id: str):
        """
        Acts as your clean data gatekeeper. It evaluates the event log
        and safely builds the production state.
        """
        # todo improve
        events = self.event_repo.get_all()
        events = [e for e in events if e.task_id == task_id]

        # Check if the execution sequence actually finished successfully
        success_event = next(
            (e for e in events if e.event_type == "DOWNLOAD_COMPLETED"), None
        )

        if not success_event:
            raise RuntimeError("No success event found")

        # Extract the verified facts from the event payload
        params = success_event.payload["download"]
        item = Download(**params)
        self.download_repo.add(item)

    def project_direct(self, params: Dict):
        item = Download(**params)
        self.download_repo.add(item)
