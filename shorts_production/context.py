from services.short_producer_service import ShortProducer
from services.downloader_service import DownloaderService
from dbs.mongo_client import get_mongo_client
from dbs.config_repository import MongoConfigRepository, MongoDownloadParamsRepository, MongoShortProductionParamsRepository
from config import MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT
from services.filename_provider import FilenameProvider
from config import TEMP_DIR

# from dbs.interfaces import InMemoryDummyRepository
# config_repo = InMemoryDummyRepository()


mongo_client = get_mongo_client(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)
config_repo = MongoConfigRepository(
    mongo_client, db_name="cc_db", collection_name="short_configs"
)
download_params_repo = MongoDownloadParamsRepository(
    mongo_client, db_name="cc_db", collection_name="download_params"
)
short_prod_params_repo = MongoShortProductionParamsRepository(
    mongo_client, db_name="cc_db", collection_name="short_prod_params"
)


downloader_service = DownloaderService(download_params_repo=download_params_repo)
raw_segments_filename_provider = FilenameProvider(
    directory=str(TEMP_DIR), suffix="segment_raw.mp4"
)
short_producer = ShortProducer(
    config_repo=config_repo,
    raw_file_provider=raw_segments_filename_provider,
    short_prod_params_repo=short_prod_params_repo,
)
