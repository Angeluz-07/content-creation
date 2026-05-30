from dbs.qdrant_client import get_qdrant_client
from dbs.qdrant_retriever import QdrantVectorRetriever
from services.embedding import EmbeddingService
from services.something import Something
from services.finder import Finder
from pathlib import Path

es = EmbeddingService()
vector_size = es.get_dimension()
collection_name = "video_segments"
client = get_qdrant_client()

qvr = QdrantVectorRetriever(client, collection_name, vector_size)
s = Something(retriever=qvr, embedder=es)
finder = Finder(retriever=qvr, embedder=es)
