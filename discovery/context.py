from dbs.qdrant_client import get_qdrant_client
from dbs.qdrant_store import QdrantVectorStore
from services.embedding import Embedder
from services.ingestion import Ingester
from services.detection import Detector
from services.transcription import GroqAudioTranscriber
from config import GROQ_API_KEY
from services.download import DownloadService

client = get_qdrant_client()
collection_name = "moments"  # change to 'moments'
embedder = Embedder()
vector_size = embedder.get_dimension()

qvs = QdrantVectorStore(client, collection_name, vector_size)
qvs.ensure_collection_exists()

transcriber = GroqAudioTranscriber(GROQ_API_KEY)
ingester = Ingester(vector_store=qvs, embedder=embedder, transcriber=transcriber)
metal_detector = Detector(vector_store=qvs, embedder=embedder)

download_service = DownloadService()
