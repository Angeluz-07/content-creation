from bson import ObjectId
from pymongo import MongoClient
from dbs.interfaces import IRepository
from typing import List, Optional, Any

class MongoConfigRepository(IRepository):
    def __init__(self, client: MongoClient, db_name: str, collection_name: str):
        self._db = client[db_name]
        self._collection = self._db[collection_name]

    # --- Métodos Privados de Mapeo ---

    def _map_to_dict(self, config_obj: Any) -> dict:
        """Convierte un objeto de dominio a un diccionario para Mongo."""
        data = config_obj.__dict__.copy()
        # Si el objeto ya tiene un ID de dominio, lo mapeamos a _id si es necesario
        if "id" in data and data["id"]:
            data["_id"] = ObjectId(data["id"])
            del data["id"]
        return data

    def _map_to_object(self, doc: dict) -> Any:
        """Convierte un documento de Mongo a un objeto de dominio."""
        if not doc:
            return None
        
        # Extraemos el _id de mongo y lo convertimos a string para el dominio
        doc["id"] = str(doc.pop("_id"))
        
        # Aquí instanciarías tu clase Config real
        # return Config(**doc) 
        return doc # Retorno temporal hasta tener tu modelo

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