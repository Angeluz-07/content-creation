from typing import Dict, Any
from fastapi import HTTPException, status
from dbs.mongo_repository import DownloadParamsMongoRepository


class DownloadValidationError(Exception):
    """Raises when a condition is not me to start a download"""

    pass


class DownloadValidatorService:
    def __init__(self, download_repo):
        self.download_repo: DownloadParamsMongoRepository = download_repo

    def validate(self, params: Dict[str, Any]) -> None:
        """
        Ejecuta todas las reglas ad-hoc de forma secuencial.
        Lanza RuleValidationError si alguna falla.
        """
        self._validate_filename_not_exists(params)

    def _validate_unique_segment(self, params: Dict[str, Any]) -> None:
        exists = self.download_repo.exists_by_segment_params(
            url=params.get("url"),
            start_segment=params.get("start_segment"),
            end_segment=params.get("end_segment"),
        )
        if exists:
            raise DownloadValidationError(
                "Ya existe una descarga programada o completada para este intervalo de tiempo."
            )

    def _validate_filename_not_exists(self, params: Dict[str, Any]) -> None:
        filename = params.get("output_filename")
        exists = self.download_repo.exists_by_filename(filename)
        if exists:
            raise DownloadValidationError(
                f"El archivo '{filename}' ya existe en la base de datos."
            )
