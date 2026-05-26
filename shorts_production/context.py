from services.short_production_service import ShortProductionService
from services.download_service import DownloadService
from services.task_service import TaskService
from services.sse_service import SSEService
from services.download_validator import DownloadValidator
from services.short_production_validator import ShortProductionValidator
from services.event_service import EventService
from services.download_projector import DownloadProjector
from services.short_production_projector import ShortProductionProjector
from dbs.mongo_client import get_mongo_client
from shorts_production.dbs.mongo_repository import DownloadMongoRepository
from shorts_production.dbs.mongo_repository import ShortProductionMongoRepository
from shorts_production.dbs.mongo_repository import TaskMongoRepository
from shorts_production.dbs.mongo_repository import EventMongoRepository

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
        mongo_client = get_mongo_client(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)
        # fmt: off
        self.download_repo = DownloadMongoRepository(client=mongo_client, db_name=MONGO_DB_NAME, collection_name="downloads")
        self.short_production_repo = ShortProductionMongoRepository(client=mongo_client, db_name=MONGO_DB_NAME, collection_name="short_productions")
        self.task_repo = TaskMongoRepository(client=mongo_client, db_name=MONGO_DB_NAME, collection_name="tasks")
        self.event_repo = EventMongoRepository(client=mongo_client, db_name=MONGO_DB_NAME, collection_name="events")
        # fmt: on


class ServiceHub:
    def __init__(self, repos: RepositoryHub):
        # fmt: off
        self.download_validator = DownloadValidator(download_repo=repos.download_repo)
        self.download_service   = DownloadService(download_repo=repos.download_repo, validator_service=self.download_validator) # exposed
        self.download_projector = DownloadProjector(event_repo=repos.event_repo, download_repo=repos.download_repo)#exposed

        self.raw_segments_filename_provider = FilenameProvider(directory=str(DOWNLOAD_DIR), suffix=".mp4") 
        self.short_prod_validator           = ShortProductionValidator(short_production_repo=repos.short_production_repo)
        self.short_producer                 = ShortProductionService(raw_file_provider= self.raw_segments_filename_provider,short_production_repo=repos.short_production_repo,validator=self.short_prod_validator) # exposed        
        self.short_production_projector     = ShortProductionProjector(event_repo=repos.event_repo, short_production_repo=repos.short_production_repo)#exposed
        
        self.event_service = EventService(event_repo=repos.event_repo)
        self.sse_service  = SSEService(redis_url=REDIS_HOST)# exposed
        self.task_service = TaskService(task_repo=repos.task_repo, download_repo=repos.download_repo, sse_service=self.sse_service) #exposed
        # fmt : on


repos = RepositoryHub()
services = ServiceHub(repos)

# fmt: off
download_service               = services.download_service
download_projector             = services.download_projector
raw_segments_filename_provider = services.raw_segments_filename_provider
short_producer                 = services.short_producer
short_production_projector     = services.short_production_projector
event_service                  = services.event_service
sse_service                    = services.sse_service
task_service                   = services.task_service
# fmt: on
