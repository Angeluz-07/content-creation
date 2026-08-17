from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / ".data"

VTT_DIR = str(DATA_DIR / "downloads" / "vtt")
VIDEO_DIR_DOWNLOAD = str(DATA_DIR / "videos" /"downloads" )
AUDIO_DIR_DOWNLOAD = str(DATA_DIR / "downloads" / "audio")
VIDEO_DIR_OUTPUT = str(DATA_DIR / "videos" /"output" )
TEMP_DIR = str(DATA_DIR / "temp")
TEMPLATES_DIR = str(DATA_DIR / "imgs" / "templates")
FONTS_DIR = str(DATA_DIR / "assets")


GOLD_SAMPLES_DIR = str(DATA_DIR / "gold_samples")
DOWNLOAD_DIR = str(DATA_DIR / "downloads")
DOWNLOAD_DIR_AUDIO = str(DATA_DIR / "downloads" / "audio")
OUTPUT_DIR = str(DATA_DIR / "output_videos")
METALS_DIR = str(DATA_DIR / "metals")
INGESTION_DIR = str(DATA_DIR / "gold_samples")

IMGS_DIR = str(DATA_DIR / "imgs")

PROMPTS_DIR = str(DATA_DIR / "prompts")

TEST_DATA_DIR = str(PROJECT_DIR / "src" / "tests" / ".data")
MONGO_DB_NAME = "cc_db"
MONGODB_URI = os.getenv("MONGODB_URI")
REDIS_URI = os.getenv("REDIS_URI")


COOKIES_PATH = str(DATA_DIR / "cookies.txt")
WEBHOOK_URI = os.getenv("WEBHOOK_URI")

QDRANTDB_URI = os.getenv("QDRANTDB_URI")
EMBEDDER_URI = os.getenv("EMBEDDER_URI")

ASSETS_DIR = str(DATA_DIR / "assets")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
