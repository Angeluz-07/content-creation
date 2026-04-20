import ollama

from prompt_repository import Prompt
from text_content_repository import TextContent
from config import DEFAULT_MODEL


class TextGenerator:
    def __init__(self, model=DEFAULT_MODEL):
        self.model = DEFAULT_MODEL

    def generate(self, prompt: Prompt):
        system_content = prompt.system_content
        user_content = prompt.user_content
        num_predict = prompt.num_predict
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            options={"num_predict": num_predict, "temperature": 0.8},
        )

        # Limpieza: Eliminamos posibles espacios en blanco extras
        historia = response["message"]["content"].strip()

        result = TextContent(
            topic=prompt.name,
            text=historia,
            num_words=len(historia.split()),
            prompt_config_id=prompt.id,
            creation_duration=float(round(response.total_duration / 1e9, 2)),
        )

        return result
