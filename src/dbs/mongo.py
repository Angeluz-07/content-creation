from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from .interfaces import IRepository
from typing import Any, List, Optional, Dict

def get_mongo_client(connection_string: str) -> MongoClient:
    """
    Genera y valida un cliente de MongoDB utilizando un string de conexión (URI).
    """
    try:
        # Inicializamos el cliente directamente con la URI recibida
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)

        # Forzamos una llamada para validar la autenticación y conexión
        client.admin.command("ping")
        return client
    except ConnectionFailure:
        raise ConnectionError(
            "No se pudo conectar a la instancia de MongoDB con el connection string proporcionado."
        )


class MongoRepository(IRepository):
    def __init__(
        self, client: MongoClient, db_name: str, collection_name: str, domain_class
    ):
        self._db = client[db_name]
        self._collection = self._db[collection_name]
        self._domain_class = domain_class

    # --- Métodos Privados de Mapeo ---

    def _map_to_dict(self, obj: Any) -> dict:
        data = obj.__dict__.copy()
        # Usamos tu UUID de dominio como el _id de Mongo
        data["_id"] = data.pop("id")
        return data

    def _map_to_object(self, doc: dict) -> Any:
        if not doc:
            return None
        # Ya no necesitas str(doc.pop("_id")) porque ya es un string
        doc["id"] = doc.pop("_id")
        return self._domain_class(**doc)

    # --- Implementación de la Interfaz ---

    def get_all(self) -> List[Any]:
        documents = self._collection.find()
        return [self._map_to_object(doc) for doc in documents]

    def get_all(self, filters: Optional[dict] = None) -> List[Any]:
        # Si no se pasan filtros, usamos un diccionario vacío para traer todo
        query = filters if filters is not None else {}
        
        # Si tu filtro busca por "id", recuerda mapearlo a "_id" para Mongo
        if "id" in query:
            query["_id"] = query.pop("id")
            
        documents = self._collection.find(query).sort("created_at", -1)
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

    def exists_by_filename(self, filename: str) -> bool:
        document = self._collection.find_one(
            {"output_filename": filename},
            projection={"_id": 1},  # <--- Eficiencia pura: solo trae el ID
        )
        return document is not None
