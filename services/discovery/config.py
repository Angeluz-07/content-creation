from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent

DATA_DIR = PROJECT_DIR / ".data"

VTT_DIR = str(DATA_DIR / "downloads" / "vtt")

OUTPUT_DIR = str(DATA_DIR / "metals" )

ENV_DIR = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_DIR)


TEST_DATA_DIR = str(PROJECT_DIR / "tests" / ".data")
PROMPT_DIR = str(DATA_DIR / "prompts")

QDRANTDB_HOST = os.getenv("QDRANTDB_HOST")
QDRANTDB_PORT = os.getenv("QDRANTDB_PORT")
QDRANTDB_URI = os.getenv("QDRANTDB_URI")
EMBEDDER_URI = os.getenv("EMBEDDER_URI")

WEBHOOK_URI = os.getenv("WEBHOOK_URI")

