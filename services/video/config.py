from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent


DATA_DIR = PROJECT_DIR / ".data"
OUTPUT_DIR = str(DATA_DIR / "output_videos")
TEMP_DIR = str(DATA_DIR / "temp")

ASSETS_DIR = str(DATA_DIR / "assets")
EMOJI_DIR = str(Path(ASSETS_DIR) / "emojis")
LAYOUT_DIR = str(Path(ASSETS_DIR) / "layouts")

DOWNLOAD_DIR = str(DATA_DIR / "downloads" / "video")

WEBHOOK_URI = os.getenv("WEBHOOK_URI")
