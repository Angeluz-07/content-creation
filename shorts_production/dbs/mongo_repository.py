from bson import ObjectId
from pymongo import MongoClient
from dbs.interfaces import IRepository
from typing import List, Optional, Any
from domain.models import DownloadParams, ShortProductionParams


class BaseMongoRepository(IRepository):
    def __init__(self, client: MongoClient, db_name: str, collection_name: str):
        self._db = client[db_name]
        self._collection = self._db[collection_name]

    # --- Métodos Privados de Mapeo ---

    def _map_to_dict(self, obj: Any) -> dict:
        data = obj.__dict__.copy()
        # Usamos tu UUID de dominio como el _id de Mongo
        data["_id"] = data.pop("id")
        return data

    def _map_to_object(self, doc: dict) -> Any:
        raise NotImplementedError

    # --- Implementación de la Interfaz ---

    def get_all(self) -> List[Any]:
        documents = self._collection.find()
        return [self._map_to_object(doc) for doc in documents]

    def add(self, entity: Any) -> None:
        doc = self._map_to_dict(entity)
        result = self._collection.insert_one(doc)
        entity.id = str(result.inserted_id)

    def get_by_id(self, entity_id: str) -> Optional[Any]:
        try:
            doc = self._collection.find_one({"_id": ObjectId(entity_id)})
            return self._map_to_object(doc)
        except Exception:
            # Manejo de IDs inválidos de MongoDB
            return None


class DownloadParamsMongoRepository(BaseMongoRepository):

    def _map_to_object(self, doc: dict) -> Any:
        if not doc:
            return None
        # Ya no necesitas str(doc.pop("_id")) porque ya es un string
        doc["id"] = doc.pop("_id")
        return DownloadParams(**doc)


class ShortProductionParamsMongoRepository(BaseMongoRepository):

    def _map_to_object(self, doc: dict) -> Any:
        if not doc:
            return None
        # Ya no necesitas str(doc.pop("_id")) porque ya es un string
        doc["id"] = doc.pop("_id")
        return ShortProductionParams(**doc)
