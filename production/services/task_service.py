from dbs.mongo_repository import TaskMongoRepository
from dbs.interfaces import IRepository
from domain.models import Task, TaskStatus
from uuid import uuid4
from typing import List, Dict
from dataclasses import asdict
from services.sse_service import SSEService
from uuid import uuid4

# todo: make method to group by target_entity_type


class TaskService:

    def __init__(self, task_repo, sse_service):
        self.task_repo: TaskMongoRepository = task_repo
        self.sse_service: SSEService = sse_service

    def get_all(self) -> List[Task]:
        result = self.task_repo.get_all()
        result.reverse()
        return result

    def get_all_filtered_by_type(self, target_entity_type: str) -> List[Dict]:
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
        print(f"updating task={task_id[:5]}, status={status}")
        self.task_repo.update_fields(task_id, {"status": status})
        print(f"updated task={task_id[:5]}, status={status}")
        self.sse_service.notify_task_update_sync(task_id, status.value)

    def mark_as_processing(self, task_id: str) -> None:
        self._update_status(task_id, TaskStatus.PROCESSING)

    def mark_as_completed(self, task_id: str) -> None:
        self._update_status(task_id, TaskStatus.COMPLETED)

    def mark_as_failed(self, task_id: str) -> None:
        self._update_status(task_id, TaskStatus.FAILED)

    def get_new_uuid(self):
        return str(uuid4())