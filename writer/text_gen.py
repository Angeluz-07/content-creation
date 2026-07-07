import os
import time
from groq import Groq


class GroqHookGenerator:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """
        Inicializa el cliente de Groq.
        Modelos recomendados para texto/velocidad en Free Tier:
        - 'llama3-8b-8192' (Ultra rápido, ideal para hooks cortos)
        - 'llama3-70b-8192' (Mayor capacidad de razonamiento)
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        
        # Pausa por defecto para proteger los límites de peticiones por minuto (RPM)
        self.SAFE_PAUSE = 4.0

    def generate_text(self, system_prompt: str, user_content: str, force_pause: float = None) -> str:
        """
        Envía las instrucciones y el texto a Groq Cloud de forma directa.
        """
        print(f"🚀 Enviando prompt a Groq usando {self.model}...")
        
        try:
            # Consumo estándar idéntico al formato OpenAI
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                temperature=0.7,
                max_tokens=100,
                top_p=1.0,
                stream=False,
            )
            
            # Control de tiempo para no saturar las cuotas del Free Tier
            pause_time = force_pause if force_pause is not None else self.SAFE_PAUSE
            if pause_time > 0:
                print(f"⏱️ Respetando cuotas de Groq. Pausa de seguridad de {pause_time}s...")
                time.sleep(pause_time)
                
            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"❌ Error en la API de Groq: {e}")
            return "¡SE DIJERON TODO! 😱"