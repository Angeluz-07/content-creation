from qdrant_client import QdrantClient
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from qdrant_client.models import VectorParams, Distance, QueryRequest
from typing import List, Dict


def get_client(uri: str):
    # 2. Conexión a Qdrant
    client = QdrantClient(url=uri)
    try:
        client.get_collections()
        return client
    except Exception as e:
        raise ConnectionError(f"No se pudo conectar a Qdrant: {e}")


class IVectorStore(ABC):

    @abstractmethod
    def add(self) -> None:
        pass

    @abstractmethod
    def search(self):
        pass

    @abstractmethod
    def search_batch(self):
        pass


class QdrantVectorStore(IVectorStore):
    def __init__(self, client, embedder, collection_name):
        self.client = client
        self.embedder = embedder
        self.collection_name = collection_name

    def create_collection(self):
        vector_size = self.embedder.vector_size
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size, distance=Distance.COSINE
                ),
            )
            print(
                f"Colección '{self.collection_name}' creada con dimensión {vector_size}"
            )
        else:
            print(
                f"Collection '{self.collection_name}' exists with dimension {vector_size}"
            )

    def add(self, id: str, text: str, metadata: Dict) -> None:
        vector = self.embedder.get_vector(text)
        self.client.upsert(
            collection_name=self.collection_name,
            points=[{"id": id, "vector": vector, "payload": metadata}],
        )

    def search(self, text: str, top_k: int = 5) -> List:
        query_vector: List[float] = self.embedder.get_vector(text)
        results = self.client.query_points(
            collection_name=self.collection_name, query=query_vector, limit=top_k
        )
        return results

    def search_batch(self, texts: List[str]) -> List:
        query_vectors: List[List[float]] = self.embedder.get_vectors(texts)
        requests = [
            QueryRequest(query=vec, limit=1, with_payload=True) for vec in query_vectors
        ]

        results = self.client.query_batch_points(
            collection_name=self.collection_name, requests=requests
        )
        return results
