from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR =  BASE_DIR / ".data" 
PROMPTS_FOLDER = DATA_DIR / "prompts"
TEXT_OUTPUT_FOLDER = DATA_DIR / "text_output"
POSTS_IN_FOLDER = DATA_DIR / "posts_in"

DEFAULT_MODEL = "gemma2:9b" # better for cc
TEST_DATA_DIR = str(PROJECT_DIR / "tests" / ".data")
PROMPT_DIR = str(DATA_DIR / "prompts")

hook_generator = GroqHookGenerator(GROQ_API_KEY)
prompt_repo = PromptRepository(PROMPT_DIR)