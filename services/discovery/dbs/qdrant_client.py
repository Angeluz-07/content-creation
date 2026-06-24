from qdrant_client import QdrantClient


def get_qdrant_client(uri: str):
    # 2. Conexión a Qdrant
    client = QdrantClient(url=uri)
    try:
        client.get_collections()
        return client
    except Exception as e:
        raise ConnectionError(f"No se pudo conectar a Qdrant: {e}")
