from dbs.mongo_repository import EventMongoRepository
from domain.models import Production
from dbs.interfaces import IRepository
from typing import Dict

class ProductionProjector:

    def __init__(self, event_repo, production_repo):
        self.event_repo: EventMongoRepository = event_repo
        self.production_repo: IRepository = production_repo

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
            (e for e in events if e.event_type == "SHORT_PRODUCTION_COMPLETED"), None
        )
        # todo review if this can optimized
        if not success_event:
            raise RuntimeError("No success event foud")

        # Extract the verified facts from the event payload
        params = success_event.payload["params"]
        item = Production(**params)
        self.production_repo.add(item)

    def project_direct(self, params: Dict):
        item = Production(**params)
        self.production_repo.add(item)
