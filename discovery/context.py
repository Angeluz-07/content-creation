from discovery.dbs.qdrant_client import get_qdrant_client
from discovery.dbs.qdrant_store import QdrantVectorStore
from discovery.services.embedding import Embedder
from discovery.services.ingestion import Ingester
from discovery.services.detection import Detector
from discovery.services.transcription import GroqAudioTranscriber
from discovery.config import GROQ_API_KEY

client = get_qdrant_client()
collection_name = "moments"  # change to 'moments'
embedder = Embedder()
vector_size = embedder.get_dimension()

qvs = QdrantVectorStore(client, collection_name, vector_size)
qvs.ensure_collection_exists()

transcriber = GroqAudioTranscriber(GROQ_API_KEY)
ingester = Ingester(vector_store=qvs, embedder=embedder, transcriber=transcriber)
metal_detector = Detector(vector_store=qvs, embedder=embedder)
