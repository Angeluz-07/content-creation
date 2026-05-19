from services.short_producer_service import ShortProducer
from services.downloader_service import DownloaderService
from services.task_service import TaskService
from dbs.mongo_client import get_mongo_client
from shorts_production.dbs.mongo_repository import DownloadParamsMongoRepository
from shorts_production.dbs.mongo_repository import ShortProductionParamsMongoRepository
from shorts_production.dbs.mongo_repository import TaskMongoRepository
from config import MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB_NAME
from services.filename_provider import FilenameProvider
from config import TEMP_DIR, DOWNLOAD_DIR

# from dbs.interfaces import InMemoryDummyRepository
# config_repo = InMemoryDummyRepository()


mongo_client = get_mongo_client(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)

# Downloads
download_params_repo = DownloadParamsMongoRepository(
    client=mongo_client, db_name=MONGO_DB_NAME, collection_name="download_params"
)
downloader_service = DownloaderService(download_params_repo=download_params_repo)

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

task_service = TaskService(task_repo=task_repo)