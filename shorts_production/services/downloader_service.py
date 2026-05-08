from shorts_production.config import TEMP_DIR
from typing import Dict
from domain.services.yt_downloader import YTDownloader


class DownloaderService:
    def __init__(self, yt_downloader: YTDownloader = None):
        self.yt_downloader = yt_downloader or YTDownloader(output_path=str(TEMP_DIR))

    def run(self, params: Dict):
        url = params["url"]
        start_ts = params["start_segment"]
        end_ts = params["end_segment"]
        force_download = params["force_download"]
        filename = params["filename"]

        result_filepath = self.yt_downloader.get_video_segment(
            url, start_ts, end_ts, force_download, filename
        )
