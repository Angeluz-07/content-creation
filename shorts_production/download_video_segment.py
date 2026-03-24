import yt_dlp
import random
import time


def download_segment_from_yt(start_ts: str, end_ts: str, url: str, output_path: str):
    # Convertir "00:01:00" a segundos para la API nativa
    def to_seconds(ts):
        h, m, s = map(int, ts.split(":"))
        return h * 3600 + m * 60 + s

    start_sec = to_seconds(start_ts)
    end_sec = to_seconds(end_ts)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/mp4",
        "outtmpl": output_path,
        # Recorte nativo eficiente
        "download_ranges": lambda info_dict, ydl: [
            {
                "start_time": start_sec,
                "end_time": end_sec,
            }
        ],
        "force_keyframes_at_cuts": True,
        # Evitar bloqueos por frecuencia
        "sleep_interval": random.randint(5, 15),
        "max_sleep_interval": 30,
    }

    try:
        print(f"Starting download raw segment: {start_ts} - {end_ts}")

        start_time = time.perf_counter()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.4f} seconds")

        print("Raw segment downloaded successfuly")
    except Exception as e:
        print(f"Error while downloading: {e}")
