from pathlib import Path
import time
import asyncio
from typing import Dict
import subprocess


class YTDownloader:
    def __init__(self, output_path: str, cookies_path: str):
        self.output_path = output_path
        self.cookies_path = cookies_path

    async def run(self, params: Dict):
        url = params["url"]
        start_ts = params["start_segment"]
        end_ts = params["end_segment"]
        force_download = params["force_download"]
        output_filename = params["output_filename"]

        file_type = params["file_type"]
        if file_type == "vtt":
            result_filepath = await self.get_vtt(
                url=url,
                force_download=force_download,
                output_filename=output_filename,
            )
            print("File saved in ", result_filepath)
        elif file_type == "video":
            result_filepath = await self.get_video_segment(
                url, start_ts, end_ts, force_download, output_filename
            )
            print("File saved in ", result_filepath)
        else:
            print("Error from download service, unknown file_type")

    async def get_video_segment(
        self,
        url: str,
        start_ts: str,
        end_ts: str,
        force_download: bool,
        output_filename: str,
    ) -> str:
        raw_filepath = str(Path(self.output_path) / "video" /  f"{output_filename}.mp4")
        file_doesnt_exist = not Path(raw_filepath).is_file()

        if file_doesnt_exist or force_download:
            print(
                f"File doesnt exist or force_download={force_download}, downloading..."
            )
            await self._download_segment_from_yt(start_ts, end_ts, url, raw_filepath)
        else:
            print(f"File exists, force_download={force_download}, skipping download...")
        return raw_filepath

    async def _download_segment_from_yt(
        self, start_ts: str, end_ts: str, url: str, output_path: str
    ):
        print(
            f"Starting download raw segment (via Async Subprocess): {start_ts} - {end_ts}"
        )

        # fmt: off
        command = [
            "yt-dlp", url,
            "--external-downloader-args", "ffmpeg:-loglevel error", # hides extra logs
            "--postprocessor-args", "ffmpeg:-loglevel error",  # hides extra logs
            "--force-overwrites",
            #"--list-formats", # for debug only
            "--no-playlist",
            "--cookies", self.cookies_path,
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            # Filter 1080/720
            "-f", "bestvideo[height=1080]+bestaudio/bestvideo[height=720]+bestaudio/best[height=1080]/best[height=720]",
            "--download-sections", f"*{start_ts}-{end_ts}",
            "--force-keyframes-at-cuts",
            "-o", output_path,
            "--merge-output-format", "mp4",
            "--extractor-args", "youtube:player_client=default",
            #"--verbose",  # for debug only
        ]
        # fmt: on
        try:
            start_time = time.perf_counter()

            process = await asyncio.create_subprocess_exec(
                command[0],
                *command[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Esperamos a que el proceso muera físicamente en el Kernel
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=process.returncode,
                    cmd=command,  # O la variable donde guardes el comando ejecutado
                    stderr=stderr.decode().strip(),
                )

            end_time = time.perf_counter()
            print(f"Elapsed time: {end_time - start_time:.4f} seconds")
            print("Raw segment downloaded successfully via Async Subprocess")

        except Exception as e:
            print(f"General error or process failure: {e}")
            raise e

    async def get_vtt(
        self,
        url: str,
        force_download: bool,
        output_filename: str,
    ) -> str:
        raw_filepath = str(Path(self.output_path) / "vtt" / f"{output_filename}")
        file_doesnt_exist = not Path(raw_filepath).is_file()

        if file_doesnt_exist or force_download:
            print(
                f"File doesnt exist or force_download={force_download}, downloading..."
            )
            await self._download_vtt(url, raw_filepath)
        else:
            print(f"File exists, force_download={force_download}, skipping download...")
        return raw_filepath

    async def _download_vtt(self, url: str, output_path: str):
        print(f"Starting download vtt (via Async Subprocess): {url}")

        # fmt: off
        command = [
            "yt-dlp", url,
            "--external-downloader-args", "ffmpeg:-loglevel error", # hides extra logs
            "--postprocessor-args", "ffmpeg:-loglevel error",  # hides extra logs
            "--force-overwrites",
            "--no-playlist",
            "--cookies", self.cookies_path,
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

            process = await asyncio.create_subprocess_exec(
                command[0],
                *command[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=process.returncode,
                    cmd=command,  # O la variable donde guardes el comando ejecutado
                    stderr=stderr.decode().strip(),
                )

            end_time = time.perf_counter()
            print(f"Elapsed time: {end_time - start_time:.4f} seconds")
            print("VTT downloaded successfully via Async Subprocess")

        except Exception as e:
            print(f"General error or process failure: {e}")
            raise e

    async def get_audio(
        self,
        url: str,
        force: bool,
        output: str,
        start_ts: str,
        end_ts: str,
    ) -> str:
        output_path = str(Path(self.output_path) / "audio" / f"{output}")
        file_doesnt_exist = not Path(output_path).is_file()

        if file_doesnt_exist or force:
            print(f"Downloading audio...")
            await self._download_audio(url, output_path, start_ts, end_ts)
        else:
            print(f"File exists, skipping audio download...")
        return output_path

    async def _download_audio(
        self,
        url: str,
        output_path: str,
        start_ts: str = "0",
        end_ts: str = "inf",
    ):
        print(f"Starting download audio (via Async Subprocess): {url}")

        # fmt: off
        command = [
            "yt-dlp", url,
            "--extract-audio",                           # Extract audio from video
            "--audio-format", "aac",        # Convert/extract to AAC format
            "--external-downloader-args", "ffmpeg:-loglevel error", # hides extra logs
            "--postprocessor-args", "ffmpeg:-loglevel error",  # hides extra logs
            "--force-overwrites",
            "--no-playlist",
            "--cookies", self.cookies_path,
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "--download-sections", f"*{start_ts}-{end_ts}",
            "-o", output_path,
            #"--verbose",  # for debug only
        ]
        # fmt: on

        try:
            start_time = time.perf_counter()

            process = await asyncio.create_subprocess_exec(
                command[0],
                *command[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=process.returncode,
                    cmd=command,  # O la variable donde guardes el comando ejecutado
                    stderr=stderr.decode().strip(),
                )

            end_time = time.perf_counter()
            print(f"Elapsed time: {end_time - start_time:.4f} seconds")
            print("VTT downloaded successfully via Async Subprocess")

        except Exception as e:
            print(f"General error or process failure: {e}")
            raise e
