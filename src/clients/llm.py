import os
import time
from abc import ABC, abstractmethod
from typing import Optional, Type
from pydantic import BaseModel
from groq import Groq


# =====================================================================
# INTERFAZ BASE (Abstracción clásica con Herencia)
# =====================================================================
class BaseLLMClient(ABC):
    """
    Interfaz abstracta para clientes de LLM multipropósito.
    Permite llamadas tanto de texto plano como de salidas estructuradas JSON.
    """

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_content: str,
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> ValueError | BaseModel | str:
        """
        Ejecuta una petición al LLM.

        :param system_prompt: Instrucciones del sistema.
        :param user_content: Contenido o prompt del usuario.
        :param response_model: Clase Pydantic opcional para forzar salida JSON estructurada.
        :param temperature: Control de creatividad (0.0 para máxima consistencia matemática).
        :return: Instancia del response_model si se provee, de lo contrario un string.
        """
        pass


# =====================================================================
# IMPLEMENTACIÓN CONCRETA PARA GROQ
# =====================================================================
class GroqClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        """
        Inicializa el cliente de Groq.
        Modelos recomendados:
        - 'llama-3.3-70b-specdec' / 'llama-3.3-70b-versatile' (Razonamiento / Producción)
        - 'llama3-8b-8192' (Ultra rápido para micro-tareas o pruebas rápidas)
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.SAFE_PAUSE = 60.0

    def generate(
        self,
        system_prompt: str,
        user_content: str,
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> BaseModel | str:

        print(f"🚀 [Groq] Enviando petición usando el modelo: {self.model}...")

        # 1. Configuración base de argumentos para el ChatCompletion
        kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": temperature,
            "max_tokens": 4000,
        }

        # 2. Inyección dinámica del contrato JSON si se requiere
        if response_model is not None:
            # Groq soporta el formato idéntico a OpenAI para Structured Outputs
            kwargs["response_format"] = {"type": "json_object"}
            # Es buena práctica robustecer el prompt del sistema cuando se pide JSON
            system_prompt += f"""
            \nDebes responder ESTRICTAMENTE con un objeto JSON válido que cumpla con 
            este esquema de Pydantic: {response_model.model_json_schema()}
            """
            kwargs["messages"][0]["content"] = system_prompt

        try:
            completion = self.client.chat.completions.create(**kwargs)
            raw_response = completion.choices[0].message.content.strip()

            # 3. Pausa de seguridad para el control de cuotas (Rate Limits)
            if self.SAFE_PAUSE > 0:
                print(
                    f"⏱️ Respetando cuotas de Groq. Pausa de seguridad de {self.SAFE_PAUSE}s..."
                )
                time.sleep(self.SAFE_PAUSE)

            # 4. Retorno adaptativo basado en la presencia del modelo
            if response_model is not None:
                # El SDK o el API garantizan el JSON, lo parseamos directo al modelo de Pydantic
                return response_model.model_validate_json(raw_response)

            return raw_response

        except Exception as e:
            print(f"❌ Error crítico en la ejecución del LLM: {e}")
            if response_model is not None:
                raise e  # En pipelines estructurados (Prefect) es mejor fallar rápido para activar fallbacks
            return "¡ERROR DE EJECUCIÓN EN EL BACKEND! 😱"
