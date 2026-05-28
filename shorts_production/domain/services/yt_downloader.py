from pathlib import Path
import yt_dlp
import time
import subprocess


class YTDownloader:
    def __init__(self, output_path: str):
        self.output_path = output_path

    def get_video_segment(
        self,
        url: str,
        start_ts: str,
        end_ts: str,
        force_download: bool,
        output_filename: str,
    ) -> str:
        raw_filepath = str(Path(self.output_path) / f"{output_filename}.mp4")
        file_doesnt_exist = not Path(raw_filepath).is_file()

        if file_doesnt_exist or force_download:
            print(
                f"File doesnt exist or force_download={force_download}, downloading..."
            )
            self._download_segment_from_yt(start_ts, end_ts, url, raw_filepath)
        else:
            print(f"File exists, force_download={force_download}, skipping download...")
        return raw_filepath

    def _download_segment_from_yt(
        self, start_ts: str, end_ts: str, url: str, output_path: str
    ):
        print(f"Starting download raw segment (via Subprocess): {start_ts} - {end_ts}")

        # fmt: off
        command = [
            "yt-dlp", url,
            "--external-downloader-args", "ffmpeg:-loglevel error", # hides extra logs
            "--postprocessor-args", "ffmpeg:-loglevel error",  # hides extra logs
            "--force-overwrites",
            #"--list-formats", # for debug only
            "--no-playlist",
            "--cookies", "my_cookies.txt",
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            # Filter 1080/720
            "-f", "bestvideo[height=1080]+bestaudio/bestvideo[height=720]+bestaudio/best[height=1080]/best[height=720]",
            "--download-sections", f"*{start_ts}-{end_ts}",
            "--force-keyframes-at-cuts",
            "-o", output_path,
            "--merge-output-format", "mp4",
            "--extractor-args",
            "youtube:player_client=default",
            #"--verbose",  # for debug only
        ]
        # fmt: on
        try:
            start_time = time.perf_counter()

            result = subprocess.run(command, check=True, text=True)

            end_time = time.perf_counter()
            print(f"Elapsed time: {end_time - start_time:.4f} seconds")
            print("Raw segment downloaded successfully via Subprocess")

        except subprocess.CalledProcessError as e:
            print(f"Error while downloading with subprocess: {e}")
            raise e
        except Exception as e:
            print(f"General error: {e}")
            raise e

    def get_vtt(
        self,
        url: str,
        force_download: bool,
        output_filename: str,
    ) -> str:
        raw_filepath = str(Path(self.output_path) / f"{output_filename}.vtt")
        file_doesnt_exist = not Path(raw_filepath).is_file()

        if file_doesnt_exist or force_download:
            print(
                f"File doesnt exist or force_download={force_download}, downloading..."
            )
            self._download_vtt(url, raw_filepath)
        else:
            print(f"File exists, force_download={force_download}, skipping download...")
        return raw_filepath

    def _download_vtt(self, url: str, output_path: str):
        print(f"Starting download vtt (via Subprocess): {url}")

        # fmt: off
        command = [
            "yt-dlp", url,
            "--external-downloader-args", "ffmpeg:-loglevel error", # hides extra logs
            "--postprocessor-args", "ffmpeg:-loglevel error",  # hides extra logs
            "--force-overwrites",
            "--no-playlist",
            "--cookies", "my_cookies.txt",
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "--write-subs",
            "--write-auto-sub",
            "--sub-lang", "es",
            "--skip-download",
            "--convert-subs", "vtt",
            "-o", output_path,
            #"--verbose",  # for debug only
        ]
        # fmt: on

        try:
            start_time = time.perf_counter()

            result = subprocess.run(command, check=True, text=True)

            end_time = time.perf_counter()
            print(f"Elapsed time: {end_time - start_time:.4f} seconds")
            print("Raw segment downloaded successfully via Subprocess")

        except subprocess.CalledProcessError as e:
            print(f"Error while downloading with subprocess: {e}")
            raise e
        except Exception as e:
            print(f"General error: {e}")
            raise e
