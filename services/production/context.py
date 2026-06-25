from services.production_service import ProductionService
from services.download_service import DownloadService
from services.task_service import TaskService
from services.asset import AssetProvider
from services.discovery_service import DiscoveryService
from dbs.mongo_client import get_mongo_client
from dbs.mongo_repository import DownloadMongoRepository
from dbs.mongo_repository import ProductionMongoRepository
from dbs.mongo_repository import TaskMongoRepository

from config import (
    MONGODB_URI,
    MONGO_DB_NAME,
    REDIS_URI,
)
from services.filename_provider import FilenameProvider
from config import DOWNLOAD_DIR, VTT_DIR, METALS_DIR

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
