from src.infra.dbs.qdrant import get_client
from src.infra.dbs.qdrant import QdrantVectorStore
from src.config import QDRANTDB_URI
from src.config import EMBEDDER_URI
from src.config import GROQ_API_KEY, DEEPGRAM_API_KEY
from src.config import INGESTION_DIR, PROMPTS_DIR, VTT_DIR, COOKIES_PATH
from src.infra.clients.embedding import Embedder
from src.infra.clients.transcription import (
    GroqAudioTranscriber,
    DeepgramAudioTranscriber,
)
from src.infra.dbs.md import PromptRepository
from src.config import GROQ_API_KEY, GEMINI_API_KEY
from src.infra.clients.llm import GroqClient, GeminiClient
from src.services.gen import gen_imgs as gen_imgs_

gemini_client = GeminiClient(GEMINI_API_KEY)
prompts_repo = PromptRepository(PROMPTS_DIR)

#qdrant_client = get_client(QDRANTDB_URI)
#embedder = Embedder(EMBEDDER_URI)

#collection_name = "moments"  # change to 'moments'
#qvs = QdrantVectorStore(qdrant_client, embedder, collection_name)
#qvs.create_collection()

transcriber = GroqAudioTranscriber(GROQ_API_KEY)
deepgram_transcriber = DeepgramAudioTranscriber(DEEPGRAM_API_KEY)

async def gen_imgs(url, output_filename, debug=False, force=False):
    return await gen_imgs_(
        url, output_filename, VTT_DIR, COOKIES_PATH, gemini_client, prompts_repo, debug
    )

