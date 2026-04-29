from pathlib import Path
from dotenv import load_dotenv
import os

REST_API_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = REST_API_DIR / "assets"
OUTPUT_DIR = REST_API_DIR / "output_videos"
TEMP_DIR = REST_API_DIR / "temp"

ENV_DIR = Path(__file__).resolve().parent.parent.parent / ".env"

load_dotenv(dotenv_path=ENV_DIR)

MONGO_USER=os.getenv("MONGO_USER")
MONGO_PASS=os.getenv("MONGO_PASS")
MONGO_HOST=os.getenv("MONGO_HOST")
MONGO_PORT=os.getenv("MONGO_PORT")
