from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent


DATA_DIR = PROJECT_DIR / ".data"
OUTPUT_DIR = str(DATA_DIR / "output_videos")
TEMP_DIR = str(DATA_DIR / "temp")
ASSETS_DIR = str(DATA_DIR / "assets")

DOWNLOAD_DIR = str(DATA_DIR / "downloads")

REDIS_URI = os.getenv("REDIS_URI")
