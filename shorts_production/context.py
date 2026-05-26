from services.production_service import ProductionService
from services.download_service import DownloadService
from services.task_service import TaskService
from services.sse_service import SSEService
from services.download_validator import DownloadValidator
from services.production_validator import ProductionValidator
from services.event_service import EventService
from services.download_projector import DownloadProjector
from services.production_projector import ProductionProjector
from dbs.mongo_client import get_mongo_client
from dbs.mongo_repository import DownloadMongoRepository
from dbs.mongo_repository import ProductionMongoRepository
from dbs.mongo_repository import TaskMongoRepository
from dbs.mongo_repository import EventMongoRepository

from config import (
    MONGO_USER,
    MONGO_PASS,
    MONGO_HOST,
    MONGO_PORT,
    MONGO_DB_NAME,
    REDIS_HOST,
)
from services.filename_provider import FilenameProvider
from config import TEMP_DIR, DOWNLOAD_DIR


class RepositoryHub:
    def __init__(self):
        client = get_mongo_client(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)
        # fmt: off
        self.download_repo   = DownloadMongoRepository(client=client, db_name=MONGO_DB_NAME, collection_name="downloads")
        self.production_repo = ProductionMongoRepository(client=client, db_name=MONGO_DB_NAME, collection_name="short_productions")
        self.task_repo       = TaskMongoRepository(client=client, db_name=MONGO_DB_NAME, collection_name="tasks")
        self.event_repo      = EventMongoRepository(client=client, db_name=MONGO_DB_NAME, collection_name="events")
        # fmt: on


class ServiceHub:
    def __init__(self, repos: RepositoryHub):
        # fmt: off
        self.download_validator = DownloadValidator(download_repo=repos.download_repo)
        self.download_service   = DownloadService(download_repo=repos.download_repo, validator_service=self.download_validator) # exposed
        self.download_projector = DownloadProjector(event_repo=repos.event_repo, download_repo=repos.download_repo)#exposed

        self.filename_provider    = FilenameProvider(directory=str(DOWNLOAD_DIR), suffix=".mp4") 
        self.production_validator = ProductionValidator(production_repo=repos.production_repo)
        self.production_service   = ProductionService(raw_file_provider=self.filename_provider, validator=self.production_validator) # exposed        
        self.production_projector = ProductionProjector(event_repo=repos.event_repo, production_repo=repos.production_repo)#exposed
        
        self.event_service = EventService(event_repo=repos.event_repo)
        self.sse_service  = SSEService(redis_url=REDIS_HOST)# exposed
        self.task_service = TaskService(task_repo=repos.task_repo, download_repo=repos.download_repo, sse_service=self.sse_service) #exposed
        # fmt : on


repos = RepositoryHub()
services = ServiceHub(repos)

# fmt: off
download_service               = services.download_service
download_projector             = services.download_projector
raw_segments_filename_provider = services.filename_provider
short_producer                 = services.production_service
short_production_projector     = services.production_projector
event_service                  = services.event_service
sse_service                    = services.sse_service
task_service                   = services.task_service
# fmt: on
