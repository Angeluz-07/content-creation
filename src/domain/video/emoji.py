import re
from typing import List

# 1. Diccionario optimizado con descriptores semánticos limpios
EMOJI_KEYWORDS = {
    # Chisme / Polémica
    r"(chisme|farandula|hablaron|enteraron|lengua|vibora)": "emoji_chisme",
    r"(pelea|discut|tension|callate|verdugo|critico)": "emoji_pelea",
    r"(asustado|miedo|nerviosa|tiembla)": "emoji_nervioso",
    
    # Amor / Relaciones
    r"(novia|excompañera|ex|parece|soltero|chicas)": "emoji_desamor",
    
    # Show / Competencia / Esfuerzo
    r"(materia|compet|ganar|puesto|esfuerzo|entren|rutina)": "emoji_trofeo",
    r"(puntos|equipo|remontaron|capitana|ganado)": "emoji_fuego",
    
    # Humor / Burlas locales
    r"(terrible|miau|chonchito|calzoncillo|tanga)": "emoji_risa",
    r"(lloraba|pena|lastima|triste)": "emoji_triste",
    
    # Entorno / Clima
    r"(agua|lluvia|aguacero|mojar)": "emoji_hojaalviento",
}


def extract_emoji_paths_from_text(path_getter, text: str, max_emojis: int = 3) -> List[str]:
    """
    Analiza el texto de los segmentos de video, extrae los descriptores de emojis
    más relevantes y retorna una lista con las rutas físicas de los archivos PNG/SVG.
    """
    text_lowercase = text.lower()
    found_descriptors = []
    
    # 1. Buscamos coincidencias semánticas en el texto
    for pattern, descriptor in EMOJI_KEYWORDS.items():
        if re.search(pattern, text_lowercase):
            # Usamos una lista para mantener el orden de detección pero evitando duplicados
            if descriptor not in found_descriptors:
                found_descriptors.append(descriptor)
            
            # Frenamos si alcanzamos el límite configurado (por defecto 3)
            if len(found_descriptors) >= max_emojis:
                break
                
    # 2. Fallback de seguridad: si no detecta nada, metemos el de alerta por defecto del show
    if not found_descriptors:
        found_descriptors.append("emoji_alerta")
        
    # 3. Mapeamos las llaves semánticas a rutas físicas usando tu función externa
    filepaths = [path_getter.get_path("emoji", desc) for desc in found_descriptors]
    
    return filepaths