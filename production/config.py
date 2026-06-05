from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent

DATA_DIR =  PROJECT_DIR / ".data"
#DOWNLOAD_DIR = str(DATA_DIR / "downloads")
OUTPUT_DIR = str(DATA_DIR / "output_videos")
TEMP_DIR = str(DATA_DIR / "temp")
ASSETS_DIR = str(DATA_DIR / "assets")
TEXT_FONT_PATH = str(DATA_DIR / "assets" / "ProtestStrike-Regular.ttf")

COOKIES_PATH = str(PROJECT_DIR.parent / "cookies.txt")
DOWNLOAD_DIR  =  str(PROJECT_DIR.parent / "services" / "download" / ".data" / "downloads")

ENV_DIR = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_DIR)

MONGO_USER=os.getenv("MONGO_USER")
MONGO_PASS=os.getenv("MONGO_PASS")
MONGO_HOST=os.getenv("MONGO_HOST")
MONGO_PORT=os.getenv("MONGO_PORT")
MONGO_DB_NAME="cc_db"

REDIS_HOST="redis://localhost:6379/0"