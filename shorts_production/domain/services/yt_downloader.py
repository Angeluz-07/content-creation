from pathlib import Path
import yt_dlp

import time


class YTDownloader:
    def __init__(self, output_path: str):
        self.output_path = output_path

    def get_video_segment(
        self, url: str, start_ts: str, end_ts: str, force_download: bool, file_id: str
    ) -> str:
        raw_filepath = str(Path(self.output_path) / f"{file_id}_segment_raw.mp4")
        file_doesnt_exist = not Path(raw_filepath).is_file()

        if file_doesnt_exist:
            print("File doesnt exist, downloading...")
            self._download_segment_from_yt(start_ts, end_ts, url, raw_filepath)
        elif force_download:
            print(f"File exist & force_download={force_download}, downloading...")
            file_to_remove = Path(raw_filepath)
            file_to_remove.unlink(missing_ok=True)  # delete file
            self._download_segment_from_yt(start_ts, end_ts, url, raw_filepath)
        else:
            print(
                f"Raw file exists & force_download={force_download}, skipping raw download..."
            )
        return raw_filepath

    def _download_segment_from_yt(
        self, start_ts: str, end_ts: str, url: str, output_path: str
    ):
        # Convertir "00:01:00" a segundos para la API nativa
        def to_seconds(ts):
            h, m, s = map(int, ts.split(":"))
            return h * 3600 + m * 60 + s

        start_sec = to_seconds(start_ts)
        end_sec = to_seconds(end_ts)

        ydl_opts = {
            "quiet": False,
            "no_warnings": True,
            "outtmpl": output_path,
            # CHANGE THIS: Remove the strict [ext=mp4] requirement.
            # We ask for best video + best audio and tell it to merge into mp4.
            "format": "bestvideo+bestaudio/best",
            "format_sort": ["res:4k", "ext:mp4:m4a"],
            "merge_output_format": "mp4",
            # Add this to handle the "tv downgraded" streams correctly
            "download_ranges": lambda info_dict, ydl: [
                {
                    "start_time": start_sec,
                    "end_time": end_sec,
                }
            ],
            "force_keyframes_at_cuts": True,
            # "sleep_interval": random.randint(5, 15),
            # "max_sleep_interval": 30,
            # "cookiefile": "youtube_cookies.txt",
            "extractor_args": {
                "youtube": {
                    # 'tv' or 'android' clients are great for avoiding bot-checks,
                    # but they require the broader format selection above.
                    "player_client": ["android"],
                    "player_skip": ["webpage", "configs"],
                }
            },
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
