from services.event_bus import RedisEventBus
from config import DOWNLOAD_DIR, ASSETS_DIR, OUTPUT_DIR, TEMP_DIR, EMOJI_DIR, LAYOUT_DIR
from config import REDIS_URI, REDIS_QUEUE
from domain.services.layer import LayerBuilder
from domain.services.video_builder.v2 import VideoBuilderV2
from domain.services.build.v1 import VideoBuilderV1
from services.filename_provider import FilenameProvider
from domain.services.font_provider import FontProvider
from services.production_service import ProductionService
from domain.services.build.resizer import Resizer
from services.asset import AssetProvider

resizer = Resizer(TEMP_DIR)

assets = (
    AssetProvider()
    .add_source("input", DOWNLOAD_DIR, extension=".mp4")
    .add_source("font", ASSETS_DIR, extension=".ttf")    
    .add_source("emoji", EMOJI_DIR, extension=".png")    
    .add_source("layout", LAYOUT_DIR, extension=".png")
)

layer_builder = LayerBuilder(TEMP_DIR)

video_builder = VideoBuilderV1(OUTPUT_DIR, TEMP_DIR)
filename_provider = FilenameProvider(DOWNLOAD_DIR, suffix=".mp4")
assets_provider = FilenameProvider(ASSETS_DIR, suffix=".png")
fontpath_provider = FontProvider(ASSETS_DIR)
event_bus = RedisEventBus(REDIS_URI)

production_service = ProductionService(
    video_builder, filename_provider, fontpath_provider, assets_provider
)
