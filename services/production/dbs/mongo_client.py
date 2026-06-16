from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def get_mongo_client(connection_string: str) -> MongoClient:
    """
    Genera y valida un cliente de MongoDB utilizando un string de conexión (URI).
    """    
    try:
        # Inicializamos el cliente directamente con la URI recibida
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Forzamos una llamada para validar la autenticación y conexión
        client.admin.command('ping')
        return client
    except ConnectionFailure:
        raise ConnectionError("No se pudo conectar a la instancia de MongoDB con el connection string proporcionado.")