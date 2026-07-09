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
