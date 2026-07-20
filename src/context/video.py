from src.config import  OUTPUT_DIR, TEMP_DIR
from src.domain.video.extractor import Extractor
from src.domain.video.assembler import Assembler
from src.services.video.build import *
from src.context.common import assets


assembler = Assembler(TEMP_DIR, OUTPUT_DIR)
extractor = Extractor(TEMP_DIR)

vb4 = BuilderV4(assets=assets, assembler=assembler, extractor=extractor)