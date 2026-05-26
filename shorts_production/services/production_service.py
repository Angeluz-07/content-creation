from pathlib import Path
import sys

grandparent = Path(__file__).parent.parent.parent
sys.path.append(str(grandparent))
# INFO: the code above is to be able to import config.py from higher level folder

from dbs.interfaces import IRepository

from shorts_production.config import TEMP_DIR
from shorts_production.config import ASSETS_DIR
from shorts_production.config import TEXT_FONT_PATH
from shorts_production.config import OUTPUT_DIR

from domain.services.yt_downloader import YTDownloader
from domain.services.video_builder import VideoBuilderV2
from domain.services.font_provider import FontProvider
from services.filename_provider import FilenameProvider
from uuid import uuid4


class ProductionService:
    def __init__(
        self,
        yt_downloader: YTDownloader = None,
        video_builder: VideoBuilderV2 = None,
        raw_file_provider: FilenameProvider = None,
        validator=None,
    ):
        self.yt_downloader = yt_downloader

        default_video_builder = VideoBuilderV2(
            output_path=str(OUTPUT_DIR),
            temp_path=str(TEMP_DIR),
            font_path=str(TEXT_FONT_PATH),
            assets_path=str(ASSETS_DIR),
        )
        self.video_builder = video_builder or default_video_builder
        self.font_provider = FontProvider(str(ASSETS_DIR))

        self.raw_file_provider = raw_file_provider

        self.validator = validator

    def run(self, params):
        print("Processing ", params["input_filename"])

        # fmt: off
        font_name         = params["font_name"]
        filename          = params["input_filename"]
        file_id           = filename
        watermark_text    = params["watermark_text"]
        hook_text         = params["hook_text"]
        debug_video_frame = params["debug_video_frame"]
        frame_ts          = params["frame_ts"]
        output_filename   = params["output_filename"]

        self.video_builder.font_path = self.font_provider.get_font(font_name)
        input_filepath = self.raw_file_provider.get_filepath(filename)
        result_path    = self.video_builder.build(
            input_filepath, file_id, watermark_text, hook_text, debug_video_frame, frame_ts, output_filename
        )

        print("Video produced at ", result_path)

        # fmt: on

    def get_new_uuid(self):
        return str(uuid4())
