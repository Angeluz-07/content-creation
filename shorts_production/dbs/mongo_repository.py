from bson import ObjectId
from pymongo import MongoClient
from dbs.interfaces import IRepository
from typing import List, Optional, Any, Dict
from domain.models import Download, Production, Task, Event


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
        return entity

    def get_by_id(self, entity_id: str) -> Optional[Any]:
        try:
            doc = self._collection.find_one({"_id": entity_id})
            return self._map_to_object(doc)
        except Exception:
            # Manejo de IDs inválidos de MongoDB
            return None

    # ---- Extra methods ---
    def update_fields(self, entity_id: str, fields: Dict[str, Any]) -> bool:
        """
        example usage: self.update_fields("id_123", {"path": "/vid.mp4", "size": 1024})
        """
        result = self._collection.update_one({"_id": entity_id}, {"$set": fields})
        return result.matched_count > 0


class DownloadMongoRepository(BaseMongoRepository):

    def _map_to_object(self, doc: dict) -> Any:
        if not doc:
            return None
        # Ya no necesitas str(doc.pop("_id")) porque ya es un string
        doc["id"] = doc.pop("_id")
        return Download(**doc)

    def exists_by_segment_params(
        self, url: str, start_segment: str, end_segment: str
    ) -> bool:
        document = self._collection.find_one(
            {"url": url, "start_segment": start_segment, "end_segment": end_segment},
            projection={"_id": 1},  # <--- Eficiencia pura: solo trae el ID
        )
        return document is not None

    def exists_by_filename(self, filename: str) -> bool:
        document = self._collection.find_one(
            {"output_filename": filename},
            projection={"_id": 1},  # <--- Eficiencia pura: solo trae el ID
        )
        return document is not None


class ProductionMongoRepository(BaseMongoRepository):

    def _map_to_object(self, doc: dict) -> Any:
        if not doc:
            return None
        # Ya no necesitas str(doc.pop("_id")) porque ya es un string
        doc["id"] = doc.pop("_id")
        return Production(**doc)

    def exists_by_filename(self, filename: str) -> bool:
        document = self._collection.find_one(
            {"output_filename": filename},
            projection={"_id": 1},  # <--- Eficiencia pura: solo trae el ID
        )
        return document is not None


class TaskMongoRepository(BaseMongoRepository):

    def _map_to_object(self, doc: dict) -> Any:
        if not doc:
            return None
        # Ya no necesitas str(doc.pop("_id")) porque ya es un string
        doc["id"] = doc.pop("_id")
        return Task(**doc)

class EventMongoRepository(BaseMongoRepository):

    def _map_to_object(self, doc: dict) -> Any:
        if not doc:
            return None
        # Ya no necesitas str(doc.pop("_id")) porque ya es un string
        doc["id"] = doc.pop("_id")
        return Event(**doc)
