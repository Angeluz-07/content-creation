from typing import Dict
from dbs.interfaces import IRepository
from uuid import uuid4
import requests


class DiscoveryService:
    def __init__(
        self,
        download_repo: IRepository = None,
    ):
        self.download_repo = download_repo
        self.url = "http://localhost:8004"

    def trigger(self, data: Dict):
        response = requests.post(
            f"{self.url}/discovery",
            json=data,
        )

    def get_new_uuid(self):
        return str(uuid4())
