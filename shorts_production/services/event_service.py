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
    
    # #todo move
    # def project_events_to_download(self, task_id: str) -> None:
    #     """
    #     Acts as your clean data gatekeeper. It evaluates the event log 
    #     and safely builds the production state.
    #     """
    #     # todo improve
    #     events = self.event_repo.get_all()
    #     events = [e for e in events if e.target_id == task_id]
        
    #     # Check if the execution sequence actually finished successfully
    #     success_event = next((e for e in events if e.event_type == "DOWNLOAD_COMPLETED"), None)
        
    #     if not success_event:
    #         # No success event means it either failed or is running. Do nothing.
    #         return

    #     # Extract the verified facts from the event payload
    #     target_id = success_event.payload["target_id"]
    #     params = success_event.payload["params"]
        
    #     # Safely insert the complete, clean record into your production collections
    #     self.downloader_service.save_final_download_record(target_id, params)