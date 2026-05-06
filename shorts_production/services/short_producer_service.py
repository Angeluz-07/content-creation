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

from domain.models import Config
from domain.services.yt_downloader import YTDownloader
from domain.services.video_builder import VideoBuilder


class ShortProducer:
    def __init__(
        self,
        config_repo: IRepository,
        yt_downloader: YTDownloader = None,
        video_builder: VideoBuilder = None,
    ):
        self.config_repo = config_repo
        self.yt_downloader = yt_downloader or YTDownloader(output_path=str(TEMP_DIR))

        default_video_builder = VideoBuilder(
            output_path=str(TEMP_DIR),
            font_path=str(TEXT_FONT_PATH),
            assets_path=str(ASSETS_DIR),
            output_path_=str(OUTPUT_DIR),
        )
        self.video_builder = video_builder or default_video_builder

    def run(self, config_dict):
        c = Config(**config_dict)
        print("Processing ", c.url)

        # fmt: off

        url               = c.url
        start_ts          = c.start_segment
        end_ts            = c.end_segment
        force_download    =  c.force_download
        file_id           = c.outname
        watermark_text    = c.watermark_text
        hook_text         = c.hook_text # todo improve
        debug_video_frame = c.debug_video_frame

        input_filepath = self.yt_downloader.get_video_segment(url,start_ts,end_ts,force_download,file_id)   
        result_path    = self.video_builder.build(input_filepath, file_id, watermark_text, hook_text, debug_video_frame)

        # fmt: on

        if not debug_video_frame:
            pass
            # print("Saving config repo...")
            # self.config_repo.add(c)
