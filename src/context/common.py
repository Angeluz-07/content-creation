from src.services.video.asset import AssetProvider
from src.config import (
    DOWNLOAD_DIR_VIDEO,
    ASSETS_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    EMOJI_DIR,
    LAYOUT_DIR,
)

assets = (
    AssetProvider()
    .add_source("temp", TEMP_DIR)
    .add_source("output_videos", OUTPUT_DIR, extension=".mp4")
    .add_source("input", DOWNLOAD_DIR_VIDEO, extension=".mp4")
    .add_source("font", ASSETS_DIR, extension=".ttf")
    .add_source("emoji", EMOJI_DIR, extension=".png")
    .add_source("layout", LAYOUT_DIR, extension=".png")
)
