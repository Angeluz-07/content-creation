from pathlib import Path
import yt_dlp
import time
import subprocess


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
        print(f"Starting download raw segment (via Subprocess): {start_ts} - {end_ts}")

        # El comando exacto que validamos en consola
        command = [
            "yt-dlp",
            url,
            # "--list-formats", #for debug only
            "--cookies",
            "my_cookies.txt",
            "--js-runtimes",
            "node",
            "--remote-components",
            "ejs:github",
            # Formato: Tu filtro de 1080/720
            "-f",
            "bestvideo[height=1080][ext=mp4]+bestaudio[ext=m4a] / bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a] / best[height=1080][ext=mp4] / best[height=720][ext=mp4]",
            # Segmento: Usamos --download-sections con sintaxis de tiempo
            "--download-sections",
            f"*{start_ts}-{end_ts}",
            "--force-keyframes-at-cuts",
            "-o",
            output_path,
            "--merge-output-format",
            "mp4",
            # Evitar SABR forzando clientes móviles
            "--extractor-args",
            "youtube:player_client=web,tv",
            "--verbose",  # Mantener para debug
        ]

        try:
            start_time = time.perf_counter()

            # Ejecutamos y capturamos salida para loguear si es necesario
            result = subprocess.run(command, check=True, text=True)

            end_time = time.perf_counter()
            print(f"Elapsed time: {end_time - start_time:.4f} seconds")
            print("Raw segment downloaded successfully via Subprocess")

        except subprocess.CalledProcessError as e:
            print(f"Error while downloading with subprocess: {e}")
        except Exception as e:
            print(f"General error: {e}")
