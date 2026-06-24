from dbs.qdrant_client import get_qdrant_client
from dbs.qdrant_store import QdrantVectorStore
from config import QDRANTDB_HOST, QDRANTDB_PORT, QDRANTDB_URI
from config import EMBEDDER_URI
from config import VTT_DIR, OUTPUT_DIR
from services.embedding import Embedder
from services.detection import Detector

client = get_qdrant_client( QDRANTDB_URI)
collection_name = "moments"  # change to 'moments'

embedder = Embedder(EMBEDDER_URI)
embedder.wait_until_ready()
vector_size = embedder.get_dimension()

qvs = QdrantVectorStore(client, collection_name, vector_size)
qvs.ensure_collection_exists()

metal_detector = Detector(
    vector_store=qvs, embedder=embedder, vtt_dir=VTT_DIR, output_dir=OUTPUT_DIR
)
