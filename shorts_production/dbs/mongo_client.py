import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def get_mongo_client(user, password, host, port) -> MongoClient:
    """
    Genera un cliente de MongoDB utilizando variables de entorno.
    """    
    # Construcción de la URI (formato estándar)
    uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Forzamos una llamada para validar la conexión
        client.admin.command('ping')
        return client
    except ConnectionFailure:
        raise ConnectionError("No se pudo conectar a la instancia de MongoDB local.")