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
from config import TEMP_DIR, DOWNLOAD_DIR, OUTPUT_DIR, ASSETS_DIR, COOKIES_PATH
from domain.services.video_builder.v2 import VideoBuilderV2
from domain.services.font_provider import FontProvider
from domain.services.yt_downloader import YTDownloader


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
    def __init__(self, r: RepositoryHub):
        download_repo = r.download_repo
        production_repo = r.production_repo
        task_repo = r.task_repo
        event_repo = r.event_repo

        # fmt: off
        download_validator      = DownloadValidator(download_repo)
        yt_downloader           = YTDownloader(DOWNLOAD_DIR, COOKIES_PATH)
        self.download_service   = DownloadService(download_repo, download_validator, yt_downloader) 
        self.download_projector = DownloadProjector(event_repo, download_repo) 

        video_builder             = VideoBuilderV2(OUTPUT_DIR, TEMP_DIR)
        self.filename_provider    = FilenameProvider(DOWNLOAD_DIR, suffix=".mp4") 
        fontpath_provider         = FontProvider(ASSETS_DIR)
        production_validator      = ProductionValidator(production_repo)
        self.production_service   = ProductionService(video_builder, self.filename_provider, fontpath_provider, production_validator)
        self.production_projector = ProductionProjector(event_repo, production_repo)
        
        self.event_service = EventService(event_repo)
        self.sse_service   = SSEService(redis_url=REDIS_HOST)
        self.task_service  = TaskService(task_repo, self.sse_service)
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
