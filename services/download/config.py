from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent

DATA_DIR = PROJECT_DIR / ".data"
DOWNLOAD_DIR = str(DATA_DIR / "downloads")

COOKIES_PATH = str(DATA_DIR / "cookies.txt")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_NAME = "cc_db"
