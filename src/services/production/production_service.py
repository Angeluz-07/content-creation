from uuid import uuid4
from typing import Dict
import requests
from src.domain.production.models import Production


class ProductionValidationError(Exception):
    """Raises when a condition is not me to start a video production"""

    pass


class ProductionService:
    def __init__(
        self,
        production_repo,
    ):
        self.production_repo = production_repo

    def project(self, params: Dict):
        item = Production(**params)
        self.production_repo.add(item)

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
        exists = self.production_repo.exists_by_filename(filename)
        if exists:
            raise ProductionValidationError(
                f"El archivo '{filename}' ya existe en la base de datos."
            )
