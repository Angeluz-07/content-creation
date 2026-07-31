from src.infra.dbs.qdrant import get_client
from src.infra.dbs.qdrant import QdrantVectorStore
from src.config import  QDRANTDB_URI
from src.config import EMBEDDER_URI
from src.config import GROQ_API_KEY
from src.config import INGESTION_DIR
from src.services.discovery.embedding import Embedder
from src.services.discovery.ingestion import Ingester
from src.infra.clients.transcription import GroqAudioTranscriber
from src.services.discovery.detection import DetectorV2
from src.infra.context.common import assets

qdrant_client = get_client(QDRANTDB_URI)
embedder = Embedder(EMBEDDER_URI)

collection_name = "moments"  # change to 'moments'
qvs = QdrantVectorStore(qdrant_client, embedder, collection_name)
qvs.create_collection()

metal_detector = DetectorV2(assets, qvs)

transcriber = GroqAudioTranscriber(GROQ_API_KEY)
ingester = Ingester(vector_store=qvs, embedder=embedder, transcriber=transcriber, ingestion_dir=INGESTION_DIR)

