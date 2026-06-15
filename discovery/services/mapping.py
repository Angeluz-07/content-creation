from datetime import datetime, timedelta
import math


def format_time(time_str, round_fn, extra_sec=0):
    # Convertimos el string en un objeto timedelta para manipularlo fácilmente
    t = datetime.strptime(time_str, "%H:%M:%S.%f")
    seconds = t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000
    # Aplicamos el redondeo (piso o techo) y los segundos extra
    final_seconds = round_fn(seconds) + extra_sec
    return str(timedelta(seconds=final_seconds)).zfill(8)

def map_discovery_results(result, prefix, url):
    # Fecha de hoy en formato AAAAMMDD
    today = datetime.now().strftime("%Y%m%d")

    # Mapeo compacto en una sola línea de comprensión (list comprehension)
    mapped_data = [
        {
            "start_segment": format_time(item['start'], math.floor),
            "end_segment": format_time(item['end'], math.ceil, extra_sec=1),
            "text": item['full_context'],
            "output_filename": f"{prefix}_{today}_{idx:02d}",
            "force_download": False,
            "url": url
        }
        for idx, item in enumerate(result)
    ]
    return mapped_data

