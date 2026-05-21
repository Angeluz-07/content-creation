from dbs.mongo_repository import TaskEventMongoRepository
from domain.models import TaskEvent
from typing import Dict


class EventService:
    def __init__(self, event_repo):
        self.event_repo: TaskEventMongoRepository = event_repo
        
    def add_event(self, task_id: str, event_type: str, payload: Dict):
        self.event_repo.add(
            TaskEvent(task_id=task_id, event_type=event_type, payload=payload)
        )
   