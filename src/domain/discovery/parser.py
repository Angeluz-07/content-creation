import webvtt
import re

def parse_vtt(file_path):
    resultado = []
    bloque_anterior = set()  # Mantenemos el set para búsquedas rápidas

    for caption in webvtt.read(file_path):
        texto = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>|</?c>", "", caption.text)
        texto = texto.replace("&nbsp;", " ")
        lineas_actuales = [l.strip() for l in re.findall(r"\S.+", texto)]
        lineas_nuevas = [l for l in lineas_actuales if l not in bloque_anterior]

        if lineas_nuevas:
            sentence = " ".join(lineas_nuevas)
            resultado.append(
                {"start": caption.start, "end": caption.end, "text": sentence}
            )
        bloque_anterior = set(lineas_actuales)

    return resultado

def format_to_text_block(text_segments):
    return ""