from services.event_bus import RedisEventBus
from config import DOWNLOAD_DIR, ASSETS_DIR, OUTPUT_DIR, TEMP_DIR
from config import REDIS_URI, REDIS_QUEUE
from domain.services.video_builder.v2 import VideoBuilderV2
from services.filename_provider import FilenameProvider
from domain.services.font_provider import FontProvider
from services.production_service import ProductionService

video_builder = VideoBuilderV2(OUTPUT_DIR, TEMP_DIR)
filename_provider = FilenameProvider(DOWNLOAD_DIR, suffix=".mp4") 
fontpath_provider = FontProvider(ASSETS_DIR)
event_bus = RedisEventBus(REDIS_URI)

production_service   = ProductionService(video_builder, filename_provider, fontpath_provider)
