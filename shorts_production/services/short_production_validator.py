from typing import Dict, Any
from fastapi import HTTPException, status
from dbs.mongo_repository import ShortProductionParamsMongoRepository


class ShortProductionValidationError(Exception):
    """Raises when a condition is not me to start a download"""

    pass


class ShortProductionValidator:
    def __init__(self, short_prod_repo):
        self.short_prod_repo: ShortProductionParamsMongoRepository = short_prod_repo

    def validate(self, params: Dict[str, Any]) -> None:
        """
        Ejecuta todas las reglas ad-hoc de forma secuencial.
        Lanza RuleValidationError si alguna falla.
        """
        self._validate_filename_not_exists(params)

    def _validate_filename_not_exists(self, params: Dict[str, Any]) -> None:
        filename = params.get("output_filename")
        exists = self.short_prod_repo.exists_by_filename(filename)
        if exists:
            raise ShortProductionValidationError(
                f"El archivo '{filename}' ya existe en la base de datos."
            )
