import asyncio
from pathlib import Path
from typing import Any, Dict, Protocol
from src.domain.common import run_subprocess, run_async_subprocess
import time


def remove_middle_extension(file_path: Path) -> Path:
    """Limpia extensiones intermedias como '.es.vtt' -> '.vtt'"""
    if len(file_path.suffixes) >= 2:
        new_path = file_path.with_name(
            f"{file_path.stem.split('.')[0]}{file_path.suffix}"
        )
        if file_path.exists():
            file_path.rename(new_path)
        return new_path
    return file_path


# --- INTERFAZ (PROTOCOL) ---
class MediaDownloader(Protocol):
    def run(self, params: Dict[str, Any]) -> Path:
        pass

    async def run_async(self, params: Dict[str, Any]) -> Path:
        pass


# --- IMPLEMENTACIONES INDIVIDUALES ---


class VideoDownloader:
    def __init__(self, output_dir: Path, cookies_path: str):
        self.output_dir = output_dir / "video"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_path = cookies_path

    def _build_command(
        self, url: str, start_ts: str, end_ts: str, output_path: Path
    ) -> list:
        filter_720 = "bestvideo[height=720]+bestaudio/best[height=720]"
        #filter = "bestvideo+bestaudio"
        # fmt: off
        return [
            "yt-dlp", url,
            "--external-downloader-args", "ffmpeg:-loglevel error",
            "--postprocessor-args", "ffmpeg:-loglevel error",
            "--force-overwrites",
            #"--list-formats", # for debug only
            "--no-playlist",
            "--cookies", self.cookies_path,
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "-f", filter_720,
            "--download-sections", f"*{start_ts}-{end_ts}",
            "--force-keyframes-at-cuts",
            "-o",
            str(output_path),
            "--merge-output-format", "mp4",
            "--extractor-args", "youtube:player_client=default",
        ]
        # fmt: on

    def run(self, params: Dict[str, Any]) -> Path:
        output_path = self.output_dir / f"{params['output_filename']}.mp4"
        if not output_path.is_file() or params.get("force_download", False):
            cmd = self._build_command(
                params["url"],
                params["start_segment"],
                params["end_segment"],
                output_path,
            )
            run_subprocess(cmd)
        return output_path

    async def run_async(self, params: Dict[str, Any]) -> Path:
        output_path = self.output_dir / f"{params['output_filename']}.mp4"
        if not output_path.is_file() or params.get("force_download", False):
            cmd = self._build_command(
                params["url"],
                params["start_segment"],
                params["end_segment"],
                output_path,
            )
            await run_async_subprocess(cmd)
        return output_path


class VTTDownloader:
    def __init__(self, output_dir: Path, cookies_path: str):
        self.output_dir = output_dir / "vtt"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_path = cookies_path

    def _build_command(self, url: str, output_path: Path) -> list:
        # fmt: off
        return [
            "yt-dlp", url,
            "--external-downloader-args", "ffmpeg:-loglevel error",
            "--postprocessor-args", "ffmpeg:-loglevel error",
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
            "-o",
            str(output_path),
        ]

    def run(self, params: Dict[str, Any]) -> Path:
        output_path = self.output_dir / f"{params['output_filename']}.vtt"
        if not output_path.is_file() or params.get("force_download", False):
            cmd = self._build_command(params["url"], output_path)
            run_subprocess(cmd)
        raw_vtt = Path(f"{output_path}.es.vtt")
        return remove_middle_extension(raw_vtt)

    async def run_async(self, params: Dict[str, Any]) -> Path:
        output_path = self.output_dir / f"{params['output_filename']}"
        if not output_path.is_file() or params.get("force_download", False):
            cmd = self._build_command(params["url"], output_path)
            await run_async_subprocess(cmd)
        raw_vtt = Path(f"{output_path}.es.vtt")
        return remove_middle_extension(raw_vtt)


class AudioDownloader:
    def __init__(self, output_dir: Path, cookies_path: str):
        self.output_dir = output_dir / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_path = cookies_path

    def _build_ytdlp_command(self, url: str, output_path: Path) -> list:
        # fmt: off
        return [
            "yt-dlp", url,
            "--extract-audio",
            "--audio-format", "m4a",
            "-f", "wa[ext=m4a]",
            "--external-downloader-args", "ffmpeg:-loglevel error",
            "--postprocessor-args", "ExtractAudio:-c:a aac -ac 1 -b:a 48k -af aresample=async=1",
            "--force-overwrites",
            "--no-playlist",
            "--cookies", self.cookies_path,
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "-o", str(output_path),
        ]

    def _build_ffmpeg_command(
        self, input_audio: Path, output_segment: Path, start_ts: str, end_ts: str
    ) -> list:
        return [
            "ffmpeg",
            "-y",
            "-ss",
            start_ts,
            "-to",
            end_ts,
            "-i",
            str(input_audio),
            "-c:a",
            "copy",
            str(output_segment),
        ]

    def run(self, params: Dict[str, Any]) -> Path:
        output_path = self.output_dir / params["output_filename"]
        if not output_path.is_file() or params.get("force_download", False):
            cmd_ytdlp = self._build_ytdlp_command(params["url"], output_path)
            run_subprocess(cmd_ytdlp)

            # input_audio = Path(f"{output_path}.m4a")
            # output_segment = input_audio.parent / f"{input_audio.stem}_segment.m4a"
            # cmd_ffmpeg = self._build_ffmpeg_command(
            #     input_audio,
            #     output_segment,
            #     params["start_segment"],
            #     params["end_segment"],
            # )
            # run_subprocess(cmd_ffmpeg)
        return Path(f"{output_path}.m4a")

    async def run_async(self, params: Dict[str, Any]) -> Path:
        output_path = self.output_dir / params["output_filename"]
        if not output_path.is_file() or params.get("force_download", False):
            cmd_ytdlp = self._build_ytdlp_command(params["url"], output_path)
            await run_async_subprocess(cmd_ytdlp)

            # input_audio = Path(f"{output_path}.m4a")
            # output_segment = input_audio.parent / f"{input_audio.stem}_segment.m4a"
            # cmd_ffmpeg = self._build_ffmpeg_command(
            #     input_audio,
            #     output_segment,
            #     params["start_segment"],
            #     params["end_segment"],
            # )
            # await run_async_subprocess(cmd_ffmpeg)
        return output_path


# --- ORQUESTRADOR ---


class YTDownloader:
    def __init__(self, output_path: str, cookies_path: str):
        self.base_dir = Path(output_path)
        self.downloaders: Dict[str, MediaDownloader] = {
            "video": VideoDownloader(self.base_dir, cookies_path),
            "vtt": VTTDownloader(self.base_dir, cookies_path),
            "audio": AudioDownloader(self.base_dir, cookies_path),
        }

    def run(self, params: Dict[str, Any]) -> Path:
        file_type = params.get("file_type")
        downloader = self.downloaders.get(file_type)
        if not downloader:
            raise ValueError(f"Unknown file_type: {file_type}")

        result_filepath = downloader.run(params)
        print(f"File saved in {result_filepath}")
        return result_filepath

    async def run_async(self, params: Dict[str, Any]) -> Path:
        file_type = params.get("file_type")
        downloader = self.downloaders.get(file_type)
        if not downloader:
            raise ValueError(f"Unknown file_type: {file_type}")

        result_filepath = await downloader.run_async(params)
        print(f"File saved in {result_filepath}")
        return result_filepath

