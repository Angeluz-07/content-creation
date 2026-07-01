from src.dbs.qdrant import get_client
from src.dbs.qdrant import QdrantVectorStore
from src.config import  QDRANTDB_URI
from src.config import EMBEDDER_URI
from src.config import VTT_DIR, METALS_DIR
from src.config import GROQ_API_KEY
from src.services.discovery.embedding import Embedder
from src.services.discovery.detection import Detector
from src.services.discovery.ingestion import Ingester
from src.services.discovery.transcription import GroqAudioTranscriber

qdrant_client = get_client(QDRANTDB_URI)
collection_name = "moments"  # change to 'moments'

embedder = Embedder(EMBEDDER_URI)
embedder.wait_until_ready()
vector_size = embedder.get_dimension()

qvs = QdrantVectorStore(qdrant_client, collection_name, vector_size)
qvs.ensure_collection_exists()

metal_detector = Detector(
    vector_store=qvs, embedder=embedder, vtt_dir=VTT_DIR, output_dir=METALS_DIR
)

transcriber = GroqAudioTranscriber(GROQ_API_KEY)
ingester = Ingester(vector_store=qvs, embedder=embedder, transcriber=transcriber)
