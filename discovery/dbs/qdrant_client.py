from qdrant_client import QdrantClient


def get_qdrant_client():
    # 2. Conexión a Qdrant
    client = QdrantClient(host="localhost", port=6333)
    try:
        client.get_collections()
        return client
    except Exception as e:
        raise ConnectionError(f"No se pudo conectar a Qdrant: {e}")
