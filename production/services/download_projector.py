from dbs.interfaces import IRepository
from domain.models import Download
from typing import Dict

class DownloadProjector:

    def __init__(self, download_repo):
        self.download_repo: IRepository = download_repo

    def project_direct(self, params: Dict):
        item = Download(**params)
        self.download_repo.add(item)
