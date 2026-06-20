from config import DOWNLOAD_DIR, ASSETS_DIR, OUTPUT_DIR, TEMP_DIR, EMOJI_DIR, LAYOUT_DIR
from domain.services.layer import LayerBuilder
from domain.services.extractor import Extractor
from domain.services.assembler import Assembler
from domain.services.resizer import Resizer
from services.asset import AssetProvider
from services.build import *

resizer = Resizer(TEMP_DIR)

assets = (
    AssetProvider()
    .add_source("input", DOWNLOAD_DIR, extension=".mp4")
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
