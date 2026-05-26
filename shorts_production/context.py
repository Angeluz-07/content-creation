from services.short_producer_service import ShortProducer
from services.downloader_service import DownloadService
from services.task_service import TaskService
from services.sse_service import SSEService
from services.validator_service import DownloadValidatorService
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

# from dbs.interfaces import InMemoryDummyRepository
# config_repo = InMemoryDummyRepository()
# fmt: off
mongo_client = get_mongo_client(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)

# Downloads
download_repo = DownloadMongoRepository(client=mongo_client, db_name=MONGO_DB_NAME, collection_name="downloads")
validator_service = DownloadValidatorService(download_repo=download_repo)
download_service = DownloadService(download_repo=download_repo, validator_service=validator_service)

# Short Production
short_production_repo = ShortProductionMongoRepository(client=mongo_client, db_name=MONGO_DB_NAME, collection_name="short_productions")
raw_segments_filename_provider = FilenameProvider(directory=str(DOWNLOAD_DIR), suffix=".mp4")
short_prod_validator = ShortProductionValidator(short_production_repo=short_production_repo)
short_producer = ShortProducer(raw_file_provider=raw_segments_filename_provider,short_production_repo=short_production_repo,validator=short_prod_validator)

# Tasks
task_repo = TaskMongoRepository(client=mongo_client, db_name=MONGO_DB_NAME, collection_name="tasks")
download_repo = download_repo
sse_service = SSEService(redis_url=REDIS_HOST)
task_service = TaskService(task_repo=task_repo, download_repo=download_repo, sse_service=sse_service)

# TaskEvents
event_repo = EventMongoRepository(client=mongo_client, db_name=MONGO_DB_NAME, collection_name="events")
event_service = EventService(event_repo=event_repo)

# Projectors
download_repo = download_repo
download_projector = DownloadProjector(event_repo=event_repo, download_repo=download_repo)

short_prod_repo = short_production_repo
short_production_projector = ShortProductionProjector(event_repo=event_repo, short_production_repo=short_prod_repo)
# fmt: on
