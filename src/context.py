from src.services.production.production_service import ProductionService
from src.services.production.download_service import DownloadService
from src.services.production.task_service import TaskService
from src.services.production.asset import AssetProvider
from src.services.production.discovery_service import DiscoveryService
from src.dbs.mongo_client import get_mongo_client
from src.dbs.mongo_repository import DownloadMongoRepository
from src.dbs.mongo_repository import ProductionMongoRepository
from src.dbs.mongo_repository import TaskMongoRepository

from src.config import (
    MONGODB_URI,
    MONGO_DB_NAME,
    REDIS_URI,
)
from src.services.production.filename_provider import FilenameProvider
from src.config import DOWNLOAD_DIR, VTT_DIR, METALS_DIR

assets = AssetProvider().add_source("vtt", VTT_DIR, extension=".vtt").add_source("metals", METALS_DIR, extension=".json")


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
        self.filename_provider  = FilenameProvider(DOWNLOAD_DIR, suffix=".mp4") 
        self.production_service = ProductionService(production_repo)
        self.task_service       = TaskService(task_repo)
        self.discovery_service  = DiscoveryService()
        # fmt : on


repos = RepositoryHub()
services = ServiceHub(repos)

# fmt: off
download_service               = services.download_service
raw_segments_filename_provider = services.filename_provider
short_producer                 = services.production_service
task_service                   = services.task_service
discovery_service              = services.discovery_service
# fmt: on
