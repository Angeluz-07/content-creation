
from dbs.mongo_repository import TaskMongoRepository
from domain.models import Task, TaskStatus
from uuid import uuid4
from typing import List

class TaskService:

    def __init__(self, task_repo):
        self.task_repo: TaskMongoRepository = task_repo

    def get_all(self) -> List[Task]:
        return self.task_repo.get_all()

    def create_task(self, target_id: str):
        task = Task(target_id=target_id)
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

    def generate_uuid(self) -> str:
        return str(uuid4())  # ID de tu modelo de negocio de descargas