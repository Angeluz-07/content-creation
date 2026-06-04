from domain.services import YTDownloader
from services.download_service import DownloadService
from dbs.mongo_repository import DownloadMongoRepository
from dbs.mongo_client import get_mongo_client
from config import DOWNLOAD_DIR, COOKIES_PATH
from config import MONGODB_URI, MONGODB_NAME

download_validator = None
client = get_mongo_client(MONGODB_URI)
download_repo   = DownloadMongoRepository(client=client, db_name=MONGODB_NAME, collection_name="downloads")

yt_downloader      = YTDownloader(DOWNLOAD_DIR, COOKIES_PATH)
download_service   = DownloadService(download_repo, download_validator, yt_downloader)
