from discovery.dbs.qdrant_client import get_qdrant_client
from discovery.dbs.qdrant_store import QdrantVectorStore
from discovery.services.embedding import EmbeddingService
from discovery.services.something import Something
from discovery.services.detector import Detector
from pathlib import Path

es = EmbeddingService()
vector_size = es.get_dimension()
collection_name = "video_segments" # change to 'moments'
client = get_qdrant_client()

qvs = QdrantVectorStore(client, collection_name, vector_size)
qvs.ensure_collection_exists()

s = Something(retriever=qvs, embedder=es)
metal_detector = Detector(qdrant_store=qvs, embedder=es)
