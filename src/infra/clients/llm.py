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
        self.SAFE_PAUSE = 10.0

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


import os
from abc import ABC, abstractmethod
from typing import Optional, Type, Union
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Aseguramos que la interfaz abstracta esté importada
# (Asumiendo que heredas de la que definiste)
class BaseLLMClient(ABC):
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_content: str,
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Union[BaseModel, str]:
        pass


class GeminiClient(BaseLLMClient):
    """
    Cliente de Gemini adaptado para la interfaz BaseLLMClient.
    Soporta salidas estructuradas nativas utilizando esquemas de Pydantic.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        Inicializa el cliente de Gemini.
        Busca 'GEMINI_API_KEY' en las variables de entorno si no se provee explícitamente.
        """
        if not api_key:
            raise ValueError(
                "No se encontró la API Key de Gemini. "
                "Configura la variable de entorno 'GEMINI_API_KEY'"
            )
        
        # Inicializamos el cliente oficial de Google GenAI
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.safe_pause = 5.0


    def generate(
        self,
        system_prompt: str,
        user_content: str,
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Union[BaseModel, str]:
        """
        Ejecuta la llamada a Gemini y devuelve texto plano o una instancia del modelo Pydantic.
        """
        
        # 1. Configuración base del request
        config_params = {
            "system_instruction": system_prompt,
            "temperature": temperature,
        }

        # 2. Si se requiere salida estructurada JSON validada por Pydantic
        if response_model is not None:
            config_params["response_mime_type"] = "application/json"
            config_params["response_schema"] = response_model

        config = types.GenerateContentConfig(**config_params)

        try:
            # 3. Llamar a la API de Google
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_content,
                config=config,
            )
            
            if self.safe_pause > 0:
                print(
                    f"⏱️ Pausa de seguridad de {self.safe_pause}s..."
                )
                time.sleep(self.safe_pause)

            # 4. Procesar la respuesta
            if response_model is not None:
                # El SDK de Google ya garantiza que el string cumple con el esquema.
                # Lo parseamos de vuelta a la instancia de Pydantic para devolver un objeto tipado.
                return response_model.model_validate_json(response.text)
            
          

            return response.text

        except APIError as api_err:
            print(f"❌ Error en la API de Gemini: {api_err}")
            raise api_err
        except Exception as e:
            print(f"❌ Error inesperado procesando la llamada al LLM: {e}")
            raise e
        
import ollama 
class OllamaLocalClient(BaseLLMClient):
    """
    Cliente local para Ollama optimizado para ejecuciones en CPU.
    """

    def __init__(self, model: str = "llama3.2:3b"):
        """
        :param model: Recomendamos modelos ligeros como 'llama3.2:3b' o 'gemma2:2b' para CPU.
        """
        self.model = model
        # Verificamos conexión básica al inicializar
        try:
            ollama.ps()
        except Exception:
            raise ConnectionError(
                "No se pudo conectar a Ollama. ¿Está corriendo la aplicación de Ollama en tu máquina?"
            )

    def generate(
        self,
        system_prompt: str,
        user_content: str,
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1,
    ) -> Union[BaseModel, str]:
        
        # 1. Configurar los parámetros de Ollama
        options = {
            "temperature": temperature,
            "num_predict": 300,  # Limitamos físicamente la salida para no estresar la CPU
        }

        # 2. Si se requiere JSON estructurado nativo
        format_option = ""
        if response_model is not None:
            # Ollama soporta forzar JSON nativo pasándole "json" al formato
            format_option = "json"
        
        esquema_salida = {
            "type": "object",
            "properties": {
                "cortes": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "prefixItems": [
                            {"type": "integer"},  # start_id
                            {"type": "integer"}   # end_id
                        ],
                        "minItems": 2,
                        "maxItems": 2
                    }
                }
            },
            "required": ["cortes"]
        }
        try:
            print(f"🚀 [Ollama] Sending reques to model: {self.model}...")
            # Llamada directa a Ollama
            response = ollama.generate(
                model=self.model,
                system=system_prompt,
                prompt=user_content,
                format=esquema_salida,  # <--- AQUÍ OCURRE LA MAGIA EN CPU
                options={
                    "temperature": 0.0,    # Cero creatividad para máxima velocidad matemática
                    "num_predict": 150,     # Limitamos la salida física para que responda en segundos
                }
            )

            raw_text = response.get("response", "").strip()
            import json
            # Parseamos el JSON real (no carácter por carácter)
            data = json.loads(raw_text)
            return data.get("cortes", [])

        except json.JSONDecodeError:
            print(f"⚠️ Error al decodificar el JSON de Ollama. Output crudo: {raw_text}")
            return []
        except Exception as e:
            print(f"❌ Error en la ejecución: {e}")
            return []