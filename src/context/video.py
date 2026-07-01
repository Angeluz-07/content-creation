from src.config import DOWNLOAD_DIR_VIDEO, ASSETS_DIR, OUTPUT_DIR, TEMP_DIR, EMOJI_DIR, LAYOUT_DIR
from src.domain.video.layer import LayerBuilder
from src.domain.video.extractor import Extractor
from src.domain.video.assembler import Assembler
from src.domain.video.resizer import Resizer
from src.services.video.asset import AssetProvider
from src.services.video.build import *

resizer = Resizer(TEMP_DIR)

assets = (
    AssetProvider()
    .add_source("input", DOWNLOAD_DIR_VIDEO, extension=".mp4")
    .add_source("font", ASSETS_DIR, extension=".ttf")
    .add_source("emoji", EMOJI_DIR, extension=".png")
    .add_source("layout", LAYOUT_DIR, extension=".png")
)

layer_builder = LayerBuilder(TEMP_DIR)
assembler = Assembler(TEMP_DIR, OUTPUT_DIR)
extractor = Extractor(TEMP_DIR)

vb1 = BuilderV1(assets, resizer, layer_builder, assembler, extractor)
vb2 = BuilderV2(assets, resizer, layer_builder, assembler, extractor)
vb3 = BuilderV3(assets, resizer, layer_builder, assembler, extractor)
