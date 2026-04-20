from prompt_repository import PromptRepository
from text_content_repository import TextContentRepository

from text_generator_service import TextGenerator

prompt_repository = PromptRepository()
text_content_repository = TextContentRepository()

if __name__ == "__main__":
    prompt = prompt_repository.get_by_id("opinologo")
    text_content = TextGenerator().generate(prompt)
    text_content_repository.save(text_content)
    print(
        f"successfully generated in {text_content.creation_duration} -> {text_content}"
    )
