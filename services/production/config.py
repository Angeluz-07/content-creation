from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent

DATA_DIR = PROJECT_DIR / ".data"
ASSETS_DIR = str(DATA_DIR / "assets")
TEXT_FONT_PATH = str(DATA_DIR / "assets" / "ProtestStrike-Regular.ttf")

COOKIES_PATH = str(PROJECT_DIR.parent / ".data" / "cookies.txt")
DOWNLOAD_DIR = str(PROJECT_DIR.parent / ".data" / "downloads")
TEMP_DIR = str(PROJECT_DIR.parent / ".data" / "temp")
OUTPUT_DIR = str(PROJECT_DIR.parent / ".data" / "output_videos")


MONGO_DB_NAME = "cc_db"
MONGODB_URI = os.getenv("MONGODB_URI")
REDIS_URI = os.getenv("REDIS_URI")
