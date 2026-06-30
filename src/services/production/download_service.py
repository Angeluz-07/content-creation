from typing import Dict
from src.dbs.interfaces import IRepository
from uuid import uuid4
from src.domain.production.models import Download
import requests


class DownloadValidationError(Exception):
    """Raises when a condition is not me to start a download"""

    pass


class DownloadService:
    def __init__(
        self,
        download_repo: IRepository = None,
    ):
        self.download_repo = download_repo
        self.url = "http://localhost:8002"

    def trigger(self, data: Dict):
        try:
            response = requests.post(
                f"{self.url}/download",
                json=data,
            )
        except Exception as e:
            print(e)
            raise

    def get_last_download(self):
        params = self.download_repo.get_all()
        if len(params) > 0:
            return params[-1]
        return {}

    def project(self, params: Dict):
        item = Download(**params)
        self.download_repo.add(item)

    def get_new_uuid(self):
        return str(uuid4())

    def validate(self, params: Dict) -> None:
        """
        Ejecuta todas las reglas ad-hoc de forma secuencial.
        Lanza RuleValidationError si alguna falla.
        """
        self._validate_filename_not_exists(params)

    def _validate_filename_not_exists(self, params: Dict) -> None:
        filename = params.get("output_filename")
        exists = self.download_repo.exists_by_filename(filename)
        if exists:
            raise DownloadValidationError(
                f"El archivo '{filename}' ya existe en la base de datos."
            )
