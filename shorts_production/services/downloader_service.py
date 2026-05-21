from shorts_production.config import DOWNLOAD_DIR
from typing import Dict
from domain.services.yt_downloader import YTDownloader
from dbs.interfaces import IRepository
from dbs.mongo_repository import DownloadParamsMongoRepository
from domain.models import DownloadParams
from pathlib import Path
from services.validator_service import DownloadValidatorService


class DownloaderService:
    def __init__(
        self,
        yt_downloader: YTDownloader = None,
        download_params_repo: IRepository = None,
        validator_service=None,
    ):
        self.yt_downloader = yt_downloader or YTDownloader(
            output_path=str(DOWNLOAD_DIR)
        )
        self.download_params_repo: DownloadParamsMongoRepository = download_params_repo
        self.validator_service: DownloadValidatorService = validator_service

    def run(self, params: Dict):
        url = params["url"]
        start_ts = params["start_segment"]
        end_ts = params["end_segment"]
        force_download = params["force_download"]
        output_filename = params["output_filename"]

        result_filepath = self.yt_downloader.get_video_segment(
            url, start_ts, end_ts, force_download, output_filename
        )

        download = DownloadParams(**params)
        return download.id

    def get_last_download(self):
        params = self.download_params_repo.get_all()
        if len(params) > 0:
            return params[-1]
        return {}
