from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / ".data"

DOWNLOAD_DIR = str(DATA_DIR / "downloads" / "video")
TEMP_DIR = str(DATA_DIR / "temp")
OUTPUT_DIR = str(DATA_DIR/ "output_videos")
VTT_DIR = str(DATA_DIR / "downloads" / "vtt")
METALS_DIR = str(DATA_DIR /  "metals")

MONGO_DB_NAME = "cc_db"
MONGODB_URI = os.getenv("MONGODB_URI")
REDIS_URI = os.getenv("REDIS_URI")
