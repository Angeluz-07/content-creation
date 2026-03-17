import ollama
import json
import os
from datetime import datetime
from pathlib import Path

from prompt_config import PromptConfig, prompts_config_repository
from advices import advice_repository, AdviceRepo, Advice

MODELO = "gemma3:4b" # mas literario
#MODELO = "llama3.2:3b" # mas equilibrado

def generar_story(prompt_config: PromptConfig):

    response = ollama.chat(
        model=MODELO,
        messages=[
            {'role': 'system', 'content': prompt_config.system_content},
            {'role': 'user', 'content': prompt_config.user_content},
        ],
        options={'num_predict': prompt_config.num_predict, 'temperature': 0.8}
    )

    # Limpieza: Eliminamos posibles espacios en blanco extras
    historia = response['message']['content'].strip()
    
    # Guardar solo la historia
    data = {
        "tema": prompt_config.name,
        "texto": historia,
        "conteo_palabras": len(historia.split())
    }

    adv = Advice(
        topic= prompt_config.name,
        text = historia, 
        num_words=len(historia.split()),
        prompt_config_id=prompt_config.id,
        creation_duration=float(round(response.total_duration/1e9, 2))
    )


    return adv

if __name__ == "__main__":
    prompt = prompts_config_repository.get_by_id("")
    adv = generar_story(prompt)
    advice_repository.add(adv)
    print(f"successfully generated in {adv.creation_duration} -> {adv}")