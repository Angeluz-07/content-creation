from dbs.interfaces import IVectorStore
from qdrant_client.models import VectorParams, Distance
from typing import List, Dict

class QdrantVectorStore(IVectorStore):
    def __init__(self, client, collection_name, vector_size):
        self.client = client
        self.collection_name = collection_name
        self.vector_size = vector_size

    def ensure_collection_exists(self):
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=Distance.COSINE
                ),
            )
            print(
                f"Colección '{self.collection_name}' creada con dimensión {self.vector_size}"
            )
        else:
            print(
                f"Collection '{self.collection_name}' exists with dimension {self.vector_size}"
            )

    def add(self, id: str, vector: List[float], metadata: Dict) -> None:
        self.client.upsert(
            collection_name=self.collection_name,
            points=[{"id": id, "vector": vector, "payload": metadata}],
        )

    def search(self, query_vector: List[float], top_k: int = 5) -> List:
        results = self.client.query_points(
            collection_name=self.collection_name, query=query_vector, limit=top_k
        )
        return results