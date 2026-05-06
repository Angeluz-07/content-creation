from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR =  PROJECT_DIR / ".data"
ASSETS_DIR = DATA_DIR / "assets"
OUTPUT_DIR = DATA_DIR / "output_videos"
TEMP_DIR = DATA_DIR / "temp"
TEXT_FONT_PATH = ASSETS_DIR / "ProtestStrike-Regular.ttf"



ENV_DIR = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_DIR)

MONGO_USER=os.getenv("MONGO_USER")
MONGO_PASS=os.getenv("MONGO_PASS")
MONGO_HOST=os.getenv("MONGO_HOST")
MONGO_PORT=os.getenv("MONGO_PORT")
