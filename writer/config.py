from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR =  BASE_DIR / ".data" 
PROMPTS_FOLDER = DATA_DIR / "prompts"
TEXT_OUTPUT_FOLDER = DATA_DIR / "text_output"
POSTS_IN_FOLDER = DATA_DIR / "posts_in"

DEFAULT_MODEL = "gemma2:9b" # better for cc
