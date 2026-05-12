from services.short_producer_service import ShortProducer
from services.downloader_service import DownloaderService
from dbs.mongo_client import get_mongo_client
from shorts_production.dbs.mongo_repository import DownloadParamsMongoRepository, ShortProductionParamsMongoRepository
from config import MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB_NAME
from services.filename_provider import FilenameProvider
from config import TEMP_DIR, DOWNLOAD_DIR

# from dbs.interfaces import InMemoryDummyRepository
# config_repo = InMemoryDummyRepository()


mongo_client = get_mongo_client(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)
download_params_repo = DownloadParamsMongoRepository(
    mongo_client, db_name=MONGO_DB_NAME, collection_name="download_params"
)
short_prod_params_repo = ShortProductionParamsMongoRepository(
    mongo_client, db_name=MONGO_DB_NAME, collection_name="short_prod_params"
)


downloader_service = DownloaderService(download_params_repo=download_params_repo)
raw_segments_filename_provider = FilenameProvider(
    directory=str(DOWNLOAD_DIR), suffix=".mp4"
)
short_producer = ShortProducer(
    raw_file_provider=raw_segments_filename_provider,
    short_prod_params_repo=short_prod_params_repo,
)
