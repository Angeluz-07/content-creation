import requests
from typing import Dict
from uuid import uuid4


class DownloadService:
    def __init__(
        self,
    ):
        self.url = "http://localhost:8000"

    def trigger(self, params: Dict):
        url = params["url"]
        start_ts = params["start_segment"]
        end_ts = params["end_segment"]
        force_download = params["force_download"]
        output_filename = params["output_filename"]
        task_id = get_new_uuid()
        response = requests.post(
            f"{self.url}/download",
            json={
                "task_id": task_id,
                "url": url,
                "force_download": force_download,
                "start_segment": start_ts,
                "end_segment": end_ts,
                "output_filename": output_filename,
            },
        )


def get_new_uuid():
    return str(uuid4())
