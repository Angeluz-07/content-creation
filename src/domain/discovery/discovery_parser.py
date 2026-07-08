from pathlib import Path
from datetime import datetime, timedelta
import math
from typing import List


def format_time(time_str, round_fn, extra_sec=0):
    # Convertimos el string en un objeto timedelta para manipularlo fácilmente
    t = datetime.strptime(time_str, "%H:%M:%S.%f")
    seconds = t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
    # Aplicamos el redondeo (piso o techo) y los segundos extra
    final_seconds = round_fn(seconds) + extra_sec
    return str(timedelta(seconds=final_seconds)).zfill(8)


def compute_duration(start_str, end_str):
    # Calcula la diferencia entre dos strings de tiempo HH:MM:SS
    fmt = "%H:%M:%S"
    delta = datetime.strptime(end_str, fmt) - datetime.strptime(start_str, fmt)
    return str(timedelta(seconds=delta.total_seconds())).zfill(8)


def map_discovery_results(result, prefix, url):
    # Mapeo estructurado utilizando variables locales dentro de la comprensión para mayor limpieza
    mapped_data = []
    for idx, item in enumerate(result):
        start = format_time(item["start"], math.floor)
        end = format_time(item["end"], math.ceil, extra_sec=1)

        mapped_data.append(
            {
                "start_segment": start,
                "end_segment": end,
                "text": item["full_context"],
                "output_filename": f"{prefix}_{idx:02d}",
                "force_download": False,
                "url": url,
                "file_type": "video",
                "duration": compute_duration(start, end),
            }
        )

    return mapped_data


class DiscoveryParser:

    def run(self, result_candidates: List[dict], prefix, url):
        result = map_discovery_results(result_candidates, prefix, url)
        return result