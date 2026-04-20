from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_FOLDER = BASE_DIR / ".data" / "prompts"
TEXT_OUTPUT_FOLDER = BASE_DIR / ".data" / "text_output"

DEFAULT_MODEL = "gemma3:4b" # mas literario
#MODELO = "llama3.2:3b" # mas equilibrado