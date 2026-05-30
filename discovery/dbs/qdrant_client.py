from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance


def get_qdrant_client(embedding_dimension, collection_name):
    # 2. Conexión a Qdrant
    client = QdrantClient(host="localhost", port=6333)
    try:
        client.get_collections()
        return client
    except Exception as e:
        raise ConnectionError(f"No se pudo conectar a Qdrant: {e}")
