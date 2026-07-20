from src.config import DOWNLOAD_DIR_VIDEO, ASSETS_DIR, OUTPUT_DIR, TEMP_DIR, EMOJI_DIR, LAYOUT_DIR
from src.domain.video.layer import LayerBuilder
from src.domain.video.extractor import Extractor
from src.domain.video.assembler import Assembler
from src.domain.video.resizer import Resizer
from src.services.video.build import *
from src.context.common import assets

resizer = Resizer(TEMP_DIR)


layer_builder = LayerBuilder(TEMP_DIR)
assembler = Assembler(TEMP_DIR, OUTPUT_DIR)
extractor = Extractor(TEMP_DIR)

vb1 = BuilderV1(assets, resizer, layer_builder, assembler, extractor)
vb2 = BuilderV2(assets, resizer, layer_builder, assembler, extractor)
vb3 = BuilderV3(assets, resizer, layer_builder, assembler, extractor)
vb4 = BuilderV4(assets=assets, assembler=assembler, extractor=extractor)