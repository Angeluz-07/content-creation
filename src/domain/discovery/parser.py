import webvtt
import re
from src.domain.common import read_json


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


def format_seconds(secs: float) -> str:
    """
    print(format_seconds(116.2))       # Output: 00:01:56.200
    print(format_seconds(119.979996))  # Output: 00:01:59.980
    print(format_seconds(46.920))      # Output: 00:00:46.920
    """
    # Rounding first prevents edge cases like 59.9999 turning into 00:00:60.000
    m, s = divmod(round(secs, 3), 60)
    h, m = divmod(m, 60)
    return f"{int(h):02}:{int(m):02}:{s:06.3f}"


def parse_transcription(file_path):
    result = read_json(file_path)
    result = result["segments"]
    _result = []
    for seg in result:
        item = {
            "start": format_seconds(seg["start"]),
            "end": format_seconds(seg["end"]),
            "text": seg["text"],
        }
        _result.append(item)
    return _result


def compute_duration(start_ts: str, end_ts: str) -> float:
    """
    starts_ts = 00:01:56.190
    end_ts    = 00:01:56.200
    result    = 0.01
    """

    # efficient computing
    def ts_to_seconds(ts: str) -> float:
        hms, ms = ts.split(".")
        h, m, s = map(int, hms.split(":"))
        return (h * 3600) + (m * 60) + s + (int(ms) / 1000)

    duration = ts_to_seconds(end_ts) - ts_to_seconds(start_ts)
    return round(duration, 2)


def group_when_starts_with_uppercase(text_segments):
    result = []
    result.append(text_segments[0])
    for seg in text_segments[1:]:
        new_topic = seg["text"][0].isupper()
        if new_topic:
            result.append(seg)
        else:
            result[-1]["end"] = seg["end"]
            result[-1]["text"] += " " + seg["text"]

    return result


def group_when_ends_without_dot(text_segments):
    result = []
    result.append(text_segments[0])
    for seg in text_segments[1:]:
        the_topic_continues = not result[-1]["text"].endswith(".")
        if the_topic_continues:
            result[-1]["end"] = seg["end"]
            result[-1]["text"] += " " + seg["text"]
        else:
            result.append(seg)

    return result


def group_when_starts_with_connector(text_segments):
    # fmt: off
    MONOSILABOS_CONNECTORS = {"sí", "no", "ya", "uy", "ah", "eh", "ay", "ajá", "dale",}
    CONTINUITY_CONNECTORS = {
        "pero", "porque", "entonces", "aunque", "y", "o", "además",
        "también", "asimismo", "tampoco", "inclusive", "incluso", "luego", "después",
        "mientras", "ahora", "total","aparte"
    }
    SUBJECT_CONNECTORS = {
        "él", "ella", "ellos", "ellas", "este", "esta", "esto", "estos", "estas",
        "ese", "esa", "eso", "esos", "esas", "alguien", "nadie", "todos", "todas",
        "algunos", "algunas", "ninguno", "ambos", "ambas", "nosotros",
    }
    # fmt: on
    CONNECTORS = MONOSILABOS_CONNECTORS | CONTINUITY_CONNECTORS | SUBJECT_CONNECTORS

    result = []
    result.append(text_segments[0])
    for seg in text_segments[1:]:
        first_word = seg["text"].split()[0].lower().strip(". , ? ! ¿ i [ ]")
        the_topic_continues = first_word in CONNECTORS
        if the_topic_continues:
            result[-1]["end"] = seg["end"]
            result[-1]["text"] += " " + seg["text"]
        else:
            result.append(seg)

    return result


def format_to_text_block(text_segments):
    """
    text_segments = [
        {"start": "00:01:56.190", "end": "00:01:56.200", "text": "Estamos causa."},
        {"start": "00:01:56.200", "end": "00:01:58.429", "text": "Llegamos a Mecausa."}
    ]
    result =
        "[id:0][duration:0.01s] Estamos causa.\n
         [id:1][duration:2.23s] Llegamos a Mecausa."
    """

    lines = []
    for i, ts in enumerate(text_segments):
        duration = compute_duration(ts["start"], ts["end"])
        line = f"[id:{i}][duration:{duration}s] {ts["text"]}"
        lines.append(line)
    return "\n".join(lines)


def filter_by_duration(text_segments, min_sec=25.0, max_sec=70.0):
    segmentos_filtrados = []

    for seg in text_segments:

        duration = compute_duration(seg["start"], seg["end"])

        # 3. Filtrar estrictamente por tu rango de interés
        if min_sec <= duration <= max_sec:
            segmentos_filtrados.append(seg)

    return segmentos_filtrados


from .models import TextSegment


class VTTParser:

    def run(self, archivo_vtt):
        result = parse_vtt(archivo_vtt)
        result = group_when_starts_with_uppercase(result)
        result = group_when_ends_without_dot(result)
        result = group_when_starts_with_connector(result)
        result = filter_by_duration(result)
        result = [TextSegment(**values) for values in result]
        return result


class TranscriptionParser:

    def run(self, filepath: str):
        result = parse_transcription(filepath)
        result = group_when_starts_with_uppercase(result)
        result = group_when_ends_without_dot(result)
        result = group_when_starts_with_connector(result)
        # result = filter_by_duration(result)
        result = [TextSegment(**values) for values in result]
        return result
