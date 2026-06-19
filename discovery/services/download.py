import requests
from typing import Dict

class DownloadService:
    def __init__(
        self,
    ):
        self.url = "http://localhost:8002"

    def trigger(self, params: Dict):
        url = params["url"]
        start_ts = params["start_segment"]
        end_ts = params["end_segment"]
        force_download = params["force_download"]
        output_filename = params["output_filename"]

        response = requests.post(
            f"{self.url}/download-segment/prefect",
            json={
                "url": url,
                "force_download": force_download,
                "start_segment": start_ts,
                "end_segment": end_ts,
                "output_filename": output_filename,
            },
        )

