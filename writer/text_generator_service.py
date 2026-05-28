from config import DEFAULT_MODEL
from domain.models import Prompt, FewShotExample
from typing import List
from text_content_repository import TextContent #todo:improve
import ollama

class TextGenerator:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def _build_messages(self, prompt: Prompt) -> List[dict]:
        """Construye la lista de mensajes alternando user/assistant para los ejemplos."""
        messages = []
        
        # 1. Mensaje del sistema
        messages.append({"role": "system", "content": prompt.system_content})
        
        # 2. Inyectar ejemplos dinámicamente como turnos de chat reales
        for ex in prompt.examples:
            messages.append({"role": "user", "content": f"Noticia: {ex.seed}"})
            messages.append({"role": "assistant", "content": ex.post})
            
        # 3. La tarea real (La nueva semilla)
        # Usamos el mismo formato exacto que los ejemplos para mantener el patrón
        messages.append({"role": "user", "content": f"Noticia: {prompt.user_content}"})
        
        return messages

    def generate(self, prompt: Prompt) -> TextContent:
        # Construimos el payload de mensajes dinámico
        messages = self._build_messages(prompt)
        
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={
                "num_predict": prompt.num_predict,
                "temperature": prompt.temperature
            }
        )
        
        historia = response["message"]["content"].strip()
        
        # Limpieza por si el modelo repite el prefijo del patrón por inercia
        if historia.lower().startswith("post:"):
            historia = historia[5:].strip()


        duration_seconds = float(round(response.total_duration / 1e9, 2))
        return TextContent(
            topic=prompt.name,
            text=historia,
            num_words=len(historia.split()),
            prompt_config_id=prompt.id,
            creation_duration=duration_seconds,
        )