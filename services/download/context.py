from domain.services import YTDownloader
from services.event_bus import RedisEventBus
from config import DOWNLOAD_DIR, COOKIES_PATH
from config import REDIS_URI

event_bus = RedisEventBus(REDIS_URI)
downloader = YTDownloader(DOWNLOAD_DIR, COOKIES_PATH)
