from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / ".data"

DOWNLOAD_DIR = str(DATA_DIR / "downloads")
DOWNLOAD_DIR_VIDEO = str(DATA_DIR / "downloads" / "video")
DOWNLOAD_DIR_AUDIO = str(DATA_DIR / "downloads" / "audio")
TEMP_DIR = str(DATA_DIR / "temp")
OUTPUT_DIR = str(DATA_DIR / "output_videos")
VTT_DIR = str(DATA_DIR / "downloads" / "vtt")
METALS_DIR = str(DATA_DIR / "metals")
INGESTION_DIR =  str(DATA_DIR / "gold_samples")
TRANSCRIPTION_DIR = str(DATA_DIR / "transcriptions")

TEST_DATA_DIR = str(PROJECT_DIR / "src" / "tests" / ".data")
MONGO_DB_NAME = "cc_db"
MONGODB_URI = os.getenv("MONGODB_URI")
REDIS_URI = os.getenv("REDIS_URI")


COOKIES_PATH = str(DATA_DIR / "cookies.txt")
WEBHOOK_URI = os.getenv("WEBHOOK_URI")

QDRANTDB_URI = os.getenv("QDRANTDB_URI")
EMBEDDER_URI = os.getenv("EMBEDDER_URI")

ASSETS_DIR = str(DATA_DIR / "assets")
EMOJI_DIR = str(Path(ASSETS_DIR) / "emojis")
LAYOUT_DIR = str(Path(ASSETS_DIR) / "layouts")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

