from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent

DATA_DIR =  PROJECT_DIR / ".data"

ENV_DIR = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_DIR)

GROQ_API_KEY=os.getenv("GROQ_API_KEY")

TEST_DATA_DIR = str(PROJECT_DIR / "tests" / ".data")