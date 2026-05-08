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
from domain.services.video_builder import VideoBuilderV2
from domain.services.font_provider import FontProvider
from services.filename_provider import FilenameProvider


class ShortProducer:
    def __init__(
        self,
        config_repo: IRepository,
        yt_downloader: YTDownloader = None,
        video_builder: VideoBuilderV2 = None,
        raw_file_provider: FilenameProvider = None
    ):
        self.config_repo = config_repo
        self.yt_downloader = yt_downloader or YTDownloader(output_path=str(TEMP_DIR))

        default_video_builder = VideoBuilderV2(
            output_path=str(OUTPUT_DIR),
            temp_path=str(TEMP_DIR),
            font_path=str(TEXT_FONT_PATH),
            assets_path=str(ASSETS_DIR),
        )
        self.video_builder = video_builder or default_video_builder
        self.font_provider = FontProvider(str(ASSETS_DIR))

        self.raw_file_provider = raw_file_provider

    def run(self, params):
        #c = Config(**params)
        #print("Processing ", c.url)

        font_name = params["font_name"]
        filename = params["filename"]
        file_id = filename
        watermark_text = params["watermark_text"]
        hook_text = params["hook_text"]
        debug_video_frame = params["debug_video_frame"]
        frame_ts = params["frame_ts"]
        # fmt: off

        #url               = c.url
        #start_ts          = c.start_segment
        #end_ts            = c.end_segment
        #force_download    = c.force_download
        #file_id           = c.outname
        # watermark_text    = c.watermark_text
        # hook_text         = c.hook_text # todo improve
        # debug_video_frame = c.debug_video_frame
        # frame_ts          = c.frame_ts
        # font_name         = c.font_name

        #input_filepath = self.yt_downloader.get_video_segment(url,start_ts,end_ts,force_download,file_id)   
        self.video_builder.font_path = self.font_provider.get_font(font_name)
        input_filepath = self.raw_file_provider.get_filepath(filename)
        result_path    = self.video_builder.build(input_filepath, file_id, watermark_text, hook_text, debug_video_frame, frame_ts)

        print("Video produced at ", result_path)

        # fmt: on

        if not debug_video_frame:            
            print("Saving config repo...[none]")
            #self.config_repo.add(c)
