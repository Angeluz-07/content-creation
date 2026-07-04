from src.services.production.production_service import ProductionService
from src.services.production.download_service import DownloadService
from src.services.production.task_service import TaskService
from src.services.production.prefect_service import PrefectService
from src.dbs.mongo import MongoRepository
from src.dbs.mongo import get_mongo_client
from src.domain.download.models import Download
from src.domain.production.models import Production
from src.domain.production.models import Task
from src.config import (
    MONGODB_URI,
    MONGO_DB_NAME,
)
client = get_mongo_client(MONGODB_URI)
prefect_service = PrefectService()

class RepositoryHub:
    def __init__(self):
        client = get_mongo_client(MONGODB_URI)
        # fmt: off
        self.download_repo   = MongoRepository(client, MONGO_DB_NAME, "downloads", Download)
        self.production_repo = MongoRepository(client, MONGO_DB_NAME, "short_productions", Production)
        self.task_repo       = MongoRepository(client, MONGO_DB_NAME, "tasks", Task)
        # fmt: on


class ServiceHub:
    def __init__(self, r: RepositoryHub):
        download_repo = r.download_repo
        production_repo = r.production_repo
        task_repo = r.task_repo

        # fmt: off
        self.download_service   = DownloadService(download_repo) 
        self.production_service = ProductionService(production_repo)
        self.task_service       = TaskService(task_repo)
        # fmt : on


repos = RepositoryHub()
services = ServiceHub(repos)

# fmt: off
download_service               = services.download_service
short_producer                 = services.production_service
task_service                   = services.task_service
# fmt: on
