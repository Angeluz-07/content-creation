from src.dbs.interfaces import IRepository
from src.domain.production.models import Task, TaskStatus
from uuid import uuid4
from typing import List, Dict


class TaskService:

    def __init__(self, task_repo):
        self.task_repo: IRepository = task_repo

    def update_status(self, task_id: str, new_status: str):
        print("Updating task status ", task_id, new_status)
        if new_status == "RUNNING":
            self.mark_as_processing(task_id)
        elif new_status == "COMPLETED":
            # todo: project domain object by entity_type
            self.mark_as_completed(task_id)
        elif new_status == "FAILED":
            self.mark_as_failed(task_id)
        else:
            print("Unknown state for ", task_id)
    
    def get_all(self) -> List[Task]:
        result = self.task_repo.get_all()
        result.reverse()
        return result

    def get_all_filtered_by_type(self, target_entity_type: str) -> List[Dict]:
        # todo: make method to group by target_entity_type
        result: List[Task] = self.task_repo.get_all()
        result = [x for x in result if x.target_entity_type == target_entity_type]
        result.reverse()
        return result

    def create_task(self, task_id, entity_type, payload=None):
        task = Task(
            id=task_id,
            target_entity_id=payload["id"],
            target_entity_type=entity_type,
            payload=(payload or {}),
        )
        self.task_repo.add(task)
        return task

    def _update_status(self, task_id: str, status: TaskStatus) -> None:
        """Método privado que centraliza la actualización."""
        self.task_repo.update_fields(task_id, {"status": status})

    def mark_as_processing(self, task_id: str) -> None:
        self._update_status(task_id, TaskStatus.PROCESSING)

    def mark_as_completed(self, task_id: str) -> None:
        self._update_status(task_id, TaskStatus.COMPLETED)

    def mark_as_failed(self, task_id: str) -> None:
        self._update_status(task_id, TaskStatus.FAILED)

    def get_new_uuid(self):
        return str(uuid4())
