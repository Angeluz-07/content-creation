from src.domain.download.services import YTDownloader
from src.config import DOWNLOAD_DIR, COOKIES_PATH

downloader = YTDownloader(DOWNLOAD_DIR, COOKIES_PATH)
