from src.services.production.production_service import ProductionService
from src.services.production.download_service import DownloadService
from src.services.production.task_service import TaskService
from src.dbs.mongo_client import get_mongo_client
from src.dbs.mongo_repository import DownloadMongoRepository
from src.dbs.mongo_repository import ProductionMongoRepository
from src.dbs.mongo_repository import TaskMongoRepository
from src.services.production.prefect_service import PrefectService

from src.config import (
    MONGODB_URI,
    MONGO_DB_NAME,
)


prefect_service = PrefectService()

class RepositoryHub:
    def __init__(self):
        client = get_mongo_client(MONGODB_URI)
        # fmt: off
        self.download_repo   = DownloadMongoRepository(client=client, db_name=MONGO_DB_NAME, collection_name="downloads")
        self.production_repo = ProductionMongoRepository(client=client, db_name=MONGO_DB_NAME, collection_name="short_productions")
        self.task_repo       = TaskMongoRepository(client=client, db_name=MONGO_DB_NAME, collection_name="tasks")
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
