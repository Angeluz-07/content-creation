from services.short_producer_service import ShortProducer
from services.downloader_service import DownloaderService
from services.task_service import TaskService
from services.sse_service import SSEService
from services.validator_service import DownloadValidatorService
from services.event_service import EventService
from dbs.mongo_client import get_mongo_client
from shorts_production.dbs.mongo_repository import DownloadParamsMongoRepository
from shorts_production.dbs.mongo_repository import ShortProductionParamsMongoRepository
from shorts_production.dbs.mongo_repository import TaskMongoRepository
from shorts_production.dbs.mongo_repository import TaskEventMongoRepository

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


mongo_client = get_mongo_client(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)

# Downloads
download_params_repo = DownloadParamsMongoRepository(
    client=mongo_client, db_name=MONGO_DB_NAME, collection_name="download_params"
)
validator_service = DownloadValidatorService(download_repo=download_params_repo)
downloader_service = DownloaderService(
    download_params_repo=download_params_repo, validator_service=validator_service
)

# Short Production
short_prod_params_repo = ShortProductionParamsMongoRepository(
    client=mongo_client, db_name=MONGO_DB_NAME, collection_name="short_prod_params"
)
raw_segments_filename_provider = FilenameProvider(
    directory=str(DOWNLOAD_DIR), suffix=".mp4"
)
short_producer = ShortProducer(
    raw_file_provider=raw_segments_filename_provider,
    short_prod_params_repo=short_prod_params_repo,
)

# Tasks
task_repo = TaskMongoRepository(
    client=mongo_client, db_name=MONGO_DB_NAME, collection_name="tasks"
)
download_repo = download_params_repo
sse_service = SSEService(redis_url=REDIS_HOST)
task_service = TaskService(
    task_repo=task_repo, download_repo=download_repo, sse_service=sse_service
)

# TaskEvents
event_repo = TaskEventMongoRepository(
    client=mongo_client, db_name=MONGO_DB_NAME, collection_name="events"
)
event_service = EventService(event_repo=event_repo)