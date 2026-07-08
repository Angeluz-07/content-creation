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

    def get_all(self, type: str = None) -> List[Task]:
        filters = {"type": type} if type else {}
        result = self.task_repo.get_all(filters)
        return result

    def create_task(self, type, payload=None):
        payload["id"] = self.get_new_uuid()
        task = Task(
            type=type,
            payload=(payload or {}),
        )
        self.task_repo.add(task)
        return task.id

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
