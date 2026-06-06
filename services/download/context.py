from domain.services import YTDownloader
from services.event_bus import RedisEventBus, EVENTS_EMITTED
from config import DOWNLOAD_DIR, COOKIES_PATH
from config import REDIS_URI, REDIS_QUEUE

event_bus = RedisEventBus(REDIS_URI)
downloader = YTDownloader(DOWNLOAD_DIR, COOKIES_PATH)
