from typing import Dict
from dbs.interfaces import IRepository
from uuid import uuid4

import requests


class DownloadService:
    def __init__(
        self,
        download_repo: IRepository = None,
        validator_service=None,
    ):
        self.download_repo = download_repo
        self.validator_service = validator_service
        self.url = "http://localhost:8002"

    def trigger(self, params: Dict):
        url = params["url"]
        start_ts = params["start_segment"]
        end_ts = params["end_segment"]
        force_download = params["force_download"]
        output_filename = params["output_filename"]

        response = requests.post(
            f"{self.url}/download-segment",
            json={
                "url": url,
                "force_download": force_download,
                "start_segment": start_ts,
                "end_segment": end_ts,
                "output_filename": output_filename,
            },
        )

    def validate(self, params):
        self.validator_service.validate(params)

    def get_last_download(self):
        params = self.download_repo.get_all()
        if len(params) > 0:
            return params[-1]
        return {}

    def get_new_uuid(self):
        return str(uuid4())
