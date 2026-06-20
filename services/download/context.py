from domain.services import YTDownloader
from config import DOWNLOAD_DIR, COOKIES_PATH

downloader = YTDownloader(DOWNLOAD_DIR, COOKIES_PATH)
