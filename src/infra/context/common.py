from src.services.common.asset import AssetProvider
from src.config import (
    DOWNLOAD_DIR_VIDEO,
    DOWNLOAD_DIR_AUDIO,
    ASSETS_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    VTT_DIR,
    METALS_DIR,
    IMGS_DIR,
    TEMPLATES_DIR,
)

from src.domain.common_.path import DirMap, get_path as get_path_
from functools import partial
dir_map: DirMap = {"vtt": {"base_dir": VTT_DIR, "ext": ".vtt"}}

get_path = partial(get_path_, registry=dir_map)
# assets = (
#     AssetProvider()
#     .add_source("temp", TEMP_DIR)
#     .add_source("output_videos", OUTPUT_DIR, extension=".mp4")
#     .add_source("input", DOWNLOAD_DIR_VIDEO, extension=".mp4")
#     .add_source("imgs", IMGS_DIR)
#     .add_source("templates", TEMPLATES_DIR, extension=".png")
#     .add_source("font", ASSETS_DIR, extension=".ttf")
#     .add_source("vtt", VTT_DIR, extension=".vtt")
#     .add_source("metals", METALS_DIR, extension=".json")
#     .add_source("audio", DOWNLOAD_DIR_AUDIO, extension=".m4a")
#     .add_source("transcriptions", TRANSCRIPTION_DIR, extension=".json")
# )
