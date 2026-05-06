from pathlib import Path
import sys
grandparent = Path(__file__).parent.parent.parent
sys.path.append(str(grandparent))
# INFO: the code above is to be able to import config.py from higher level folder

from pathlib import Path
from dbs.interfaces import IRepository

import numpy as np
from shorts_production.config import TEMP_DIR # todo: improve
from shorts_production.config import ASSETS_DIR # todo: improve
from shorts_production.config import TEXT_FONT_PATH
from shorts_production.config import OUTPUT_DIR # todo: improve

from domain.models import Config
from domain.services.yt_downloader import YTDownloader
from domain.services.video_builder import VideoBuilder
#todo move functions to domain service


class ShortProducer:
    def __init__(self, config_repo: IRepository, yt_downloader: YTDownloader = None, video_builder: VideoBuilder = None):
        self.config_repo = config_repo
        self.yt_downloader = yt_downloader or YTDownloader(output_path=str(TEMP_DIR))
        
        default_video_builder = VideoBuilder(output_path=str(TEMP_DIR), font_path=str(TEXT_FONT_PATH), assets_path=str(ASSETS_DIR), output_path_=str(OUTPUT_DIR))
        self.video_builder = video_builder or default_video_builder

    def run(self, config_dict):
        c = Config(**config_dict)
        print("processing", c.url)
        URL = c.url
        START_SEGMENT = c.start_segment
        END_SEGMENT = c.end_segment
        FORCE_DOWNLOAD = c.force_download
        OUTPUT_NAME = c.outname

        WATERMARK_TEXT = c.watermark_text
        HOOK_TEXT = c.hook_text.replace(r'\n', '\n') # todo improve
        DEBUG_VIDEO_FRAME = c.debug_video_frame

        file_id = OUTPUT_NAME
        raw_filepath = self.yt_downloader.get_video_segment(URL,START_SEGMENT,END_SEGMENT,FORCE_DOWNLOAD,file_id)
        
        resized_filepath = self.video_builder._resize_video_segment(raw_filepath, file_id)
        frame_filepath = self.video_builder._get_video_frame(raw_filepath)
        fixed_layer_filepath = self.video_builder._generate_fixed_layer(WATERMARK_TEXT, HOOK_TEXT, frame_filepath)
        result_path = self.video_builder._assemble(resized_filepath, fixed_layer_filepath,OUTPUT_NAME,DEBUG_VIDEO_FRAME)
    
        if not DEBUG_VIDEO_FRAME:
            pass
            #print("Saving config repo...")
            #self.config_repo.add(c)

      
   
    
